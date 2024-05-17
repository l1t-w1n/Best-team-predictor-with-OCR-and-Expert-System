from PIL import Image as Image
import cv2
import numpy as np
import db_modules.current_hero as ch
from db_modules.db import DB

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
