import os
import requests
import random

def upload_random_files(url, directory, num_files=50):
    """Uploads a specified number of random files from the given directory to the specified URL."""
    
    # Get the list of all files in the directory
    files = os.listdir(directory)
    
    # Shuffle the list to randomize which files are picked
    random.shuffle(files)
    
    # Upload only the first 'num_files' after shuffling
    uploaded_count = 0
    for filename in files:
        if uploaded_count < num_files:
            file_path = os.path.join(directory, filename)
            with open(file_path, 'rb') as f:
                # Prepare the file in the correct format for the POST request
                files = {'file': (filename, f)}
                response = requests.post(url, files=files)
                if response.status_code == 200:
                    print(f"Successfully uploaded {filename}")
                    uploaded_count += 1
                else:
                    print(f"Failed to upload {filename}. Response status: {response.status_code}")
        else:
            break  # Stop once we have uploaded the desired number of files

if __name__ == '__main__':
    # Specify the URL and directory
    upload_url = 'http://127.0.0.1:5000/upload'
    directory_to_upload = './downloaded_images'
    upload_random_files(upload_url, directory_to_upload, 20)
