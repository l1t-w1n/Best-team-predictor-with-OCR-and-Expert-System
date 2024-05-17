import requests
from bs4 import BeautifulSoup
import os
import sqlite3
import glob
import re
from PIL import Image

DOWNLOAD_DIR = 'downloaded_images'

def download_image(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded: {save_path}")
    else:
        print("Failed to download the image.")

def scrape_hero_page(hero_name):
    formatted_hero_name = hero_name.replace(' ', '_')
    url = f"https://empiresandpuzzles.fandom.com/wiki/{formatted_hero_name}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', class_="image", href=True)
        for link in links:
            image_url = link['href']
            if image_url.startswith("https://static.wikia.nocookie.net") and ".gif" in image_url:
                image_url = image_url.split('/revision')[0]
                image_name = image_url.split('/')[-1]
                save_path = os.path.join(DOWNLOAD_DIR, image_name)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                download_image(image_url, save_path)
    else:
        print(f"Failed to load webpage for {hero_name}")
        
def cleanup_downloaded_images():
    # Directory where images are downloaded
    directory = DOWNLOAD_DIR
    # Pattern to match filenames containing 'Costume'
    pattern = os.path.join(directory, '*Costume*')
    # List all matching files
    files = glob.glob(pattern)
    for file in files:
        os.remove(file)
        print(f"Deleted {file}")

def rename_files():
    directory = DOWNLOAD_DIR
    pattern = os.path.join(directory, '*')
    files = glob.glob(pattern)
    for file in files:
        # Initialize new_name with the original filename
        new_name = file        
        # Remove '_-_Hero_Card' from filenames
        new_name = new_name.replace('_-_Hero_Card', '')        
        # Remove '_Hero_Card' from filenames
        new_name = new_name.replace('_Hero_Card', '')        
        # Remove '_-_Villain_Card' from filenames
        new_name = new_name.replace('_-_Villain_Card', '')        
        # Replace '%26' with '&' in filenames
        new_name = new_name.replace('%26', '&')        
        # Check if a change was made to the filename
        new_name = re.sub(r'\d+', '', new_name)
        
        if new_name != file:
            os.rename(file, new_name)
            print(f"Renamed {file} to {new_name}") 
            
def gif_to_png():
    directory = DOWNLOAD_DIR
    pattern = os.path.join(directory, '*.gif')
    files = glob.glob(pattern)
    for file in files:
        im = Image.open(file)
        png_file = file.replace('.gif', '.png')
        im.save(png_file)
        os.remove(file)
        print(f"Converted {file} to {png_file}")
        
def main():
    # Connect to SQLite database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    # Query database for all hero names
    cursor.execute("SELECT Hero_name FROM Hero")
    heroes = cursor.fetchall()
    
    # Scrape each hero's webpage
    for hero in heroes:
        hero_name = hero[0]  # extract the name from the tuple
        scrape_hero_page(hero_name)

    # Close database connection
    conn.close()

if __name__ == "__main__":
    main()
    cleanup_downloaded_images()
    rename_files()
    gif_to_png()