from PIL import Image as Image # Python Imaging Library
import pytesseract # OCR
import cv2
import numpy as np
import db_modules.current_hero as ch
from db_modules.db import DB

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe' # Path to the tesseract executable

def crop_black_border(img):
    img_array = np.array(img)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    coords = cv2.findNonZero(gray)
    x, y, w, h = cv2.boundingRect(coords)
    cropped_img = img.crop((x, y, x+w, y+h))
    return cropped_img

def resizeIm(im):
    im = crop_black_border(im)
    target_width = 1242
    target_height = 2208
    aspect_ratio = im.width / im.height

    if im.height != target_height:
        new_height = int(target_width / aspect_ratio)

        if new_height < target_height:
            # Calculate crop amount for top and bottom
            crop_amount = (im.height - new_height) // 2
            im = im.crop((0, crop_amount, im.width, im.height - crop_amount))
        else:
            # Calculate new height based on target width
            new_height = target_height
            new_width = int(new_height * aspect_ratio)
            crop_amount = (im.height - new_height) // 2
            im = im.crop((0, crop_amount, im.width, im.height - crop_amount))
    im = cropIm(im)
    im = im.resize((1242,1824))
    return im

def cropIm(im):
    target_width = 1242
    target_height = 1824
    desired_aspect_ratio = target_height / target_width

    # Calculate the aspect ratio of the original image
    aspect_ratio = im.width / im.height

    # Calculate the target height based on the aspect ratio and the target width
    new_height = int(im.width * desired_aspect_ratio)

    # Adjust crop area based on the calculated height
    crop_top = (im.height - new_height) // 2
    crop_bottom = im.height - crop_top

    # Crop the image vertically
    im = im.crop((0, crop_top, im.width, crop_bottom))

    return im

def removeNonNumberCharacters(string):
    return ''.join(filter(str.isdigit, string))

def removeNonLetterCharacters(string):
    return ''.join(filter(str.isalpha, string))

def imageSplitter(im):
    images = {}
    images['name'] = im.crop((im.width/3.33,im.height/59 ,im.width/1.4,im.height/17.7))
    images['power'] = im.crop((im.width/1.25,im.height/12,im.width/1.05,im.height/8))
    images['level'] = im.crop((im.width/10.5,im.height/1.65,im.width/4.6,im.height/1.51))
    #images['level'].show()
    images['teamcost'] = im.crop((im.width/9.6,im.height/11.5,im.width/5.9,im.height/7.5))
    images['skillLevel'] = im.crop((im.width/4,im.height/1.3,im.width/1.1,im.height/1.25))
    images['ascension'] = im.crop((im.width/1.25,im.height/1.73,im.width/1.1,im.height/1.46 ))
    images['attack'] = im.crop((im.width/3.25,im.height/1.54,im.width/2.4,im.height/1.44))
    images['defense'] = im.crop((im.width/2.18,im.height/1.56,im.width/1.75,im.height/1.44))
    images['hp'] = im.crop((im.width/1.63,im.height/1.55,im.width/1.35,im.height/1.44))
    return images

#Get 4 pixels, where each one represents a level of ascension, assign the adequate value and return the sum
def getAscension(im):
    listPixel = [(20,175),(20,130),(20,85),(20,40)]
    ascensionLevel=0

    for pixel in listPixel:
        pixelRGB=im.getpixel(pixel)
        if pixelRGB[0]>150 and pixelRGB[2]<=150: ascensionLevel+=1 #Yellow
        elif pixelRGB[0]>150 and pixelRGB[2]>150: ascensionLevel+=2 #Purple
        else: ascensionLevel+=0 #None

    return ascensionLevel

def getNumber(im):
    return removeNonNumberCharacters(getInfo(im))

def getInfo(im):
    # Grayscale, Gaussian blur, Otsu's threshold

    image3 = np.array(im) #A remettre
    #image3 = cv2.imread(im) #A retirer, juste pour les essais
    image3 = cv2.resize(image3,(200,200),fx=7,fy=7)
    gray = cv2.cvtColor(image3, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Morph open to remove noise and invert image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    invert = 255 - opening
    #print image after modifications
    #cv2.imshow('thresh', thresh)
    #cv2.imshow('opening', opening)
    #cv2.imshow('invert', invert)
    cv2.waitKey()

    # Perform text extraction
    return pytesseract.image_to_string(invert, lang='eng', config='--psm 13 --oem 3')

def getStats(images):
    stats= {}
    stats['name'] = removeNonLetterCharacters(pytesseract.image_to_string(images['name'], lang='eng', config='--psm 13 --oem 3'))
    stats['power'] = removeNonNumberCharacters(pytesseract.image_to_string(images['power'], lang='eng', config='--psm 13 --oem 3'))
    stats['level'] = getNumber(images['level'])
    stats['teamcost'] = getNumber(images['teamcost'])
    stats['skillLevel'] = getSkillLvl(images['skillLevel'])
    stats['attack'] = getNumber(images['attack'])
    stats['defense'] = getNumber(images['defense'])
    stats['health'] = getNumber(images['hp'])
    stats['ascension'] = getAscension(images['ascension'])

    if(stats['level'] == ""):
        stats['level'] = "1"

    print("Name  : ",stats['name']," \nPower : " , stats['power'] , " \nLevel : ",stats['level'],"\nTeam cost : ",stats['teamcost'] , "\nSkill Level : ",stats['skillLevel'])
    print("Attack : ",stats['attack']," Defense : ",stats['defense']," HP : ",stats['health'])
    print("Ascension : ",stats['ascension'])
    return stats

def getSkillLvl(im):
    #read the text on the im and then sort it to get the text that is of the format "x/y" with x and y being numbers
    text = pytesseract.image_to_string(im, lang='eng', config='--psm 13 --oem 3')
    text = text.split()
    res = ""
    for i in text:
        for j in i:
            if j.isnumeric():
                res += j
            elif j == "/":
                res += j
    if len(res) == 3:
        return res
    return "0/0"

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

def lectureCarte(path):
    im = Image.open(path)
    im = resizeIm(im)
    images = imageSplitter(im)
    stats = getStats(images)
    name= createHero(stats)
    return im, name


#lectureCarte("Images/hero12.jpg")
'''
print("-----------------------------------------------\n")
lectureCarte("Images/hero1.png")
print("-----------------------------------------------\n")
lectureCarte("Images/hero3.jpg")
'''