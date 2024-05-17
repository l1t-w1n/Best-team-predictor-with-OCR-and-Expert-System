from img_modules.crop_schreenshot import resizeIm
from db_modules.db import DB
import easyocr
import numpy as np
from PIL import Image
import os
import glob
import re
import db_modules.current_hero as ch

PATH_TO_SCREENSHOTS = '../screenshots/'
PATH_TO_CARDS = '../downloaded_images/'

SCHREENSHOT_COORDS = {'name': (622.5, 74.0), 
                      'power': (1046.5, 194.0), 
                      'attack': (447.0, 1225.0), 
                      'defense': (638.0, 1223.0), 
                      'health': (829.0, 1222.0), 
                      'level': (204.0, 1152.0), 
                      'skill_level': (515.0, 1428.0)
                      }

CARD_COORDS = {'name': (348.0, 46.0), 
               'power': (592.5, 119.0), 
               'attack': (238.0, 743.0), 
               'defense': (352.0, 743.0), 
               'health': (467.0, 744.0), 
               'level': (102.0, 702.0), 
               'skill_level': (269.0, 868.0)}

TARGET_CARD_SIZE = (691, 1099)
TARGET_SCHREENSHOT_SIZE = (1242, 1824)

def createHero(stats):
    try:
        with DB:
            #ch.create_current_hero_table()
            id = None
            id = DB.execute("Select id From Hero Where Hero_name='"+stats['name']+"'").fetchone()[0]
            current = ch.Current_hero(id,stats['attack'],stats['power'],stats['defense'],stats['health'],stats['level'],stats['ascension'],str(stats['skill_level']))
            current.store()
    except Exception as e:
        print(f"Error finding hero with name found by OCR: {e}")
    return stats['name']

def getAscension(im):
    # Crop the image
    im = im[int(im.shape[0] / 1.73):int(im.shape[0] / 1.46), int(im.shape[1] / 1.25):int(im.shape[1] / 1.1)]

    listPixel = [(20, 175), (20, 130), (20, 85), (20, 40)]
    ascensionLevel = 0

    for pixel in listPixel:
        pixelRGB = im[pixel[1], pixel[0]]  # Access pixel value using numpy indexing
        if pixelRGB[0] > 150 and pixelRGB[2] <= 150:
            ascensionLevel += 1  # Yellow
        elif pixelRGB[0] > 150 and pixelRGB[2] > 150:
            ascensionLevel += 2  # Purple

    return ascensionLevel


def extract_text(res, coords):
    extracted_text = {}
    for key, point in coords.items():
        for bbox, text, prob in res:
            bbox_center = (bbox[0][0] + bbox[2][0]) / 2, (bbox[0][1] + bbox[2][1]) / 2
            if point[0] > bbox[0][0] and point[0] < bbox[2][0] and point[1] > bbox[0][1] and point[1] < bbox[2][1]:
                if key == 'skill_level':
                    # Use regular expression to find fractional format like "1/2" or "3/5"
                    match = re.search(r'\d+/\d+', text)
                    if match:
                        extracted_text[key] = match.group(0)
                    else:
                        extracted_text[key] = None
                else:
                    extracted_text[key] = text
                break
    return extracted_text

def read_image(img):
    screenshot = False
    
    if img.mode != 'P' :
        screenshot = True
        img = resizeIm(img)
    else:
        img = img.resize(TARGET_CARD_SIZE)
        img_for_ascention_check = img.resize(TARGET_SCHREENSHOT_SIZE)    

    img = img.convert('RGB')
    img = np.array(img)
    
    if screenshot:        
        reader = easyocr.Reader(['fr'], gpu=True)
        res = reader.readtext(img)        
        extracted_hero = extract_text(res, SCHREENSHOT_COORDS) 
        ascention = getAscension(img)
        extracted_hero['ascension'] = ascention      
    else:
        reader = easyocr.Reader(['en'], gpu=True)
        res = reader.readtext(img)
        extracted_hero = extract_text(res, CARD_COORDS)
        
        img_for_ascention_check = img_for_ascention_check.convert('RGB')
        img_for_ascention_check = np.array(img_for_ascention_check)        
        ascention = getAscension(img_for_ascention_check)
        extracted_hero['ascension'] = ascention
    print(f"extracted_hero: {extracted_hero}")
    return extracted_hero
        
def read_and_save_image(path):
    img = Image.open(path)
    print(f"img.mode: {img.mode}")
    hero = read_image(img)
    name = createHero(hero)
    if img.mode != 'P' :
        img = resizeIm(img)
    return img, name

            
if __name__ == '__main__':
    pattern = os.path.join(PATH_TO_CARDS, '*')
    files = glob.glob(pattern)
    for file in files:
        img = Image.open(file)
        extracted_text = read_image(img)
        print('---')
        
    '''schreenshot_example = "./Images/hero12.jpg"
    card_example = "./downloaded_images/Zora.png"
    
    hero12 = read_image(schreenshot_example)
    zora = read_image(card_example)
    
    createHero(hero12)
    createHero(zora)'''
    

