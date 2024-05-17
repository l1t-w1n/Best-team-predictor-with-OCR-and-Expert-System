from flask import Flask, render_template, redirect, request, url_for, flash, jsonify
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from PIL import Image as Image
from img_modules.read_image import read_and_save_image
import sysExpert  as es
import sqlite3
import os
import json
import sys

# Initialize Flask app and configure SocketIO with CORS and logging
app = Flask(__name__)
app.secret_key = 'yo_mama'
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
sys.setrecursionlimit(100000)

# Configuration for image upload folder and max upload size limit
app.config['UPLOAD_FOLDER'] = 'static/images/cards'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure upload folder exists
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limit uploads to 50MB
DATABASE = 'data.db'

def get_db_connection():
    """Establishes a connection to the SQLite database and sets row factory to access columns by name."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def most_color(hero_names: list):
    conn = get_db_connection()
    mycursor = conn.cursor()

    if not hero_names:
        print("No hero names provided")
        conn.close()
        return None

    # Prepare placeholders for SQL query and tuple of names
    tuple_names = tuple(hero_names)
    placeholders = ', '.join('?' * len(tuple_names))
    query = f"""
    SELECT et.El_type FROM Hero h
    JOIN Elemental_type et ON h.El_type = et.id
    WHERE h.Hero_name IN ({placeholders})
    """
    mycursor.execute(query, tuple_names)
    results = mycursor.fetchall()
    
    color_count = {}
    for row in results:
        color = row['El_type']  # Fetch the element type name
        if color in color_count:
            color_count[color] += 1
        else:
            color_count[color] = 1
    conn.close()
    
    # Analyze the frequency of each color
    if not color_count:
        print("No colors found")
        return None

    # Determine if there's a tie in color frequency
    max_count = max(color_count.values())
    all_same_frequency = all(count == max_count for count in color_count.values())

    if all_same_frequency:
        return "All of the colors appear the same amount of times", -1
    else:
        most_common = max(color_count, key=color_count.get)
        return most_common, color_count[most_common]

def change_filename(old_path, new_filename, new_image):
    # Extract the directory part of the old path
    directory = os.path.dirname(old_path)
    
    # Extract the extension of the old filename
    _, extension = os.path.splitext(old_path)
    
    # Create the new path by combining the directory, new filename, and extension
    new_path = os.path.join(directory, f"{new_filename}{extension}")
    
    # Save the new image with the new filename
    new_image.save(new_path)
    
    # Rename the file if the filename is changed
    if old_path != new_path:
        os.remove(old_path)
    return new_path

@app.route("/")
def index():
    """Render the homepage."""
    return render_template("index.html")

@app.route("/your_cards")
def your_cards():
    """Fetch and display hero cards from the database in various file formats."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT Hero_name FROM Hero h\
                 JOIN Current_hero ch on h.id = ch.id')  # Retrieve hero names from database
    heroes = cur.fetchall()
    conn.close()
    
    # Directory where hero images are stored
    images_dir = app.config['UPLOAD_FOLDER']
    
    # Get a list of all files in the images directory
    available_files = os.listdir(images_dir)
    
    # Dictionary to store hero images
    image_files = []
    
    # Supported image file extensions
    image_extensions = ['.jpeg', '.jpg', '.png', '.gif']
    
    # Match hero names to files in the directory
    for hero in heroes:
        hero_name = hero['Hero_name']
        hero_image = None
        # Check for each file extension
        for ext in image_extensions:
            if f"{hero_name}{ext}" in available_files:
                hero_image = f"{hero_name}{ext}"
                break
        if hero_image:
            image_files.append(hero_image)
        else:
            # Optionally handle the case where no image is found
            print(f"No image found for {hero_name}")
            image_files.append('default_image.jpeg')  # Default image if none found
    
    return render_template('your_cards.html', images=image_files)

@app.route("/generic")
def generic():
    """Display all card images from the cards directory."""
    cards_path = os.path.join(app.static_folder, 'images/cards')
    card_images = [os.path.join('images/cards', filename) for filename in os.listdir(cards_path)]
    return render_template('generic.html', card_images=card_images)

@app.route("/add_card")
def add_card():
    """Page to add a new card, currently only displays the form."""
    return render_template("add_card.html")

@app.route("/upload", methods=['POST'])
def upload():
    """Handle the file upload via POST request. Redirect if no file is found, or save the file if valid."""
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)  # Secure the filename to prevent directory traversal attacks
        file_path = app.config['UPLOAD_FOLDER']+"/"+filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Save file to the upload folder
        im, name = read_and_save_image(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if name is not None:
            change_filename(file_path, name, im)
        else:
            error = 'Invalid card. Please upload a valid image.'
            return render_template("add_card.html", error = error)
        return redirect(url_for('index'))  # Redirect to the homepage after upload

@app.route("/search_heroes")
def search_heroes():
    query = request.args.get('query', '')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT Hero_name FROM Hero WHERE Hero_name LIKE ?', ('%' + query + '%',))
    heroes = cur.fetchall()
    conn.close()
    return jsonify([hero['Hero_name'] for hero in heroes])

@app.route("/get_hero_id")
def get_hero_id():
    hero_name = request.args.get('heroName', '')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM Hero WHERE Hero_name = ?', (hero_name,))
    hero_id = cur.fetchone()
    conn.close()
    return jsonify({'id': hero_id['id'] if hero_id else None})

@app.route("/analyze")
def analyze():
    try:
        selected_heroes = request.cookies.get('selectedHeroes')
        print("Selected Heroes from Cookie:", selected_heroes)

        if not selected_heroes:
            return jsonify({'error': 'No heroes selected'}), 400

        selected_heroes_dicts = json.loads(selected_heroes)
        selected_heroes_names = [hero['name'] for hero in selected_heroes_dicts if 'name' in hero]
        print("Hero Names:", selected_heroes_names)

        if not selected_heroes_names:
            return jsonify({'error': 'Hero list is empty'}), 400

        # Get the primary attribute of the team based on most frequent color
        CoulAdv = most_color(selected_heroes_names)[0]
        print("Most Common Color:", CoulAdv)
        result = es.launchSysExpert(CoulAdv)
        print("Result from Expert System:", result)

        if isinstance(result, str):
            return jsonify({'message': result})

        # If it's a list of hero IDs, retrieve their names and image paths
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            placeholders = ', '.join('?' for _ in result)
            query = f'SELECT Hero_name FROM Hero WHERE id IN ({placeholders})'
            cur.execute(query, result)
            hero_names = [row['Hero_name'] for row in cur.fetchall()]
            conn.close()

            # Get image paths
            images = []
            image_formats = ['jpeg', 'jpg', 'png']
            for hero_name in hero_names:
                for ext in image_formats:
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{hero_name}.{ext}")
                    if os.path.exists(image_path):
                        images.append({'name': hero_name, 'image': f'static/images/cards/{hero_name}.{ext}'})
                        break
            return jsonify({'heroes': images})

    except json.JSONDecodeError as e:
        return jsonify({"error": "Error decoding JSON: " + str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Server Error: " + str(e)}), 500



if __name__ == '__main__':
    # Run the app with SocketIO over specified host +and port
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
