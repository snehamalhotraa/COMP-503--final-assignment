"""
Authors: Mahenur Master, Nisharg Patel, Sneha Malhotra, Siddharth Patel
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""

from datetime import datetime
import sys
import os
import sqlite3
import hashlib
import requests
import image_lib  # Assuming this is a custom module for image handling

# Full paths of the image cache folder and database
script_dir = os.path.dirname(os.path.abspath(__file__))
image_cache_dir = os.path.join(script_dir, 'images')
image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')


def main():
    # Get the APOD date from the command line
    apod_date = get_apod_date()

    # Initialize the image cache
    init_apod_cache()

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Print the APOD title for user feedback
    if apod_id != 0:
        apod_title = get_all_apod_title(apod_id)
        print(f"APOD Title: {apod_title}")

        # Set the APOD as the desktop background image
        image_lib.set_desktop_background_image(apod_info['file_path'])
    else:
        print("Failed to retrieve APOD information.")


def get_apod_date():
    """Gets the APOD date from command-line arguments or defaults to today's date."""
    if len(sys.argv) > 1:
        try:
            apod_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD.")
            sys.exit(1)
    else:
        apod_date = datetime.today().date()
    return apod_date


def init_apod_cache():
    """Initializes the image cache by ensuring the directory and database exist."""
    if not os.path.exists(image_cache_dir):
        os.makedirs(image_cache_dir)

    if not os.path.exists(image_cache_db):
        with sqlite3.connect(image_cache_db) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS apod_cache (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    explanation TEXT,
                    file_path TEXT,
                    sha256 TEXT
                )
            ''')
        print("Created APOD cache database.")


def add_apod_to_cache(apod_date):
    """Adds APOD to the cache if not already present."""
    apod_data = get_apod_data_from_nasa(apod_date)
    if not apod_data:
        return 0

    image_sha256 = hashlib.sha256(apod_data['image_bytes']).hexdigest()
    apod_id = get_apod_id_from_db(image_sha256)
    if apod_id:
        print("APOD already in cache.")
        return apod_id

    file_path = determine_apod_file_path(apod_data['title'], apod_data['image_url'])
    image_lib.save_image_file(apod_data['image_bytes'], file_path)

    apod_id = add_apod_to_db(apod_data['title'], apod_data['explanation'], file_path, image_sha256)
    return apod_id


def get_apod_data_from_nasa(apod_date):
    """Fetches APOD data from NASA's API."""
    apod_url = f"https://api.nasa.gov/planetary/apod?date={apod_date.isoformat()}&api_key=DEMO_KEY"
    response = requests.get(apod_url)
    if response.status_code == 200:
        data = response.json()
        image_url = data.get('url')
        image_bytes = requests.get(image_url).content
        return {
            'title': data['title'],
            'explanation': data['explanation'],
            'image_url': image_url,
            'image_bytes': image_bytes
        }
    else:
        print("Error fetching APOD data.")
        return None


def add_apod_to_db(title, explanation, file_path, sha256):
    """Inserts APOD details into the database."""
    with sqlite3.connect(image_cache_db) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO apod_cache (title, explanation, file_path, sha256) 
            VALUES (?, ?, ?, ?)
        ''', (title, explanation, file_path, sha256))
        return cursor.lastrowid


def get_apod_id_from_db(image_sha256):
    """Retrieves the ID of the APOD from the cache by SHA-256."""
    with sqlite3.connect(image_cache_db) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM apod_cache WHERE sha256 = ?', (image_sha256,))
        result = cursor.fetchone()
        return result[0] if result else 0


def determine_apod_file_path(image_title, image_url):
    """Determines the appropriate file path for the APOD image."""
    file_ext = os.path.splitext(image_url)[-1]
    sanitized_title = ''.join(e for e in image_title if e.isalnum() or e == ' ').strip().replace(' ', '_')
    return os.path.join(image_cache_dir, sanitized_title + file_ext)


def get_apod_info(image_id):
    """Fetches APOD info from the database by its ID."""
    with sqlite3.connect(image_cache_db) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT title, explanation, file_path FROM apod_cache WHERE id = ?', (image_id,))
        result = cursor.fetchone()
        if result:
            return {
                'title': result[0],
                'explanation': result[1],
                'file_path': result[2]
            }
        return {}


def get_all_apod_title(image_id):
    """Fetches the title of the APOD from the database by its ID."""
    with sqlite3.connect(image_cache_db) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT title FROM apod_cache WHERE id = ?', (image_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return "Title not found."


# Entry point
if __name__ == '__main__':
    main()
