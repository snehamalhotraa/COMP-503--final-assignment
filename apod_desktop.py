""" 
COMP 593 - Final Project
Author=Mhenur Master, Nisharg Patel, Sneha Malhotra, Siddharth Patel

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
from datetime import date
import os
import hashlib
import sys 
import sqlite3
import ctypes
import apod_api
import image_lib
from tkinter import *
from tkinter import ttk
import re

# Full paths of the image cache folder and database
# - The image cache directory is a subdirectory of the specified parent directory.
# - The image cache database is a sqlite database located in the image cache directory.
script_dir = os.path.dirname(os.path.abspath(__file__))
image_cache_dir = os.path.join(script_dir, 'images')
image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()

    print(f"Image cache directory: {script_dir}")
    print(f"Image cache DB: {image_cache_db}")

    # Initialize the image cache
    init_apod_cache()

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['file_path'])

def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.

    Returns:
        date: APOD date
    """
    # TODO: Complete function body
    # Hint: The following line of code shows how to convert and ISO-formatted date string to a date object
    start_date = date(1995, 6, 16)
    if len(sys.argv) == 2:
        input_date = sys.argv[1]
        try:
            apod_date = date.fromisoformat(input_date)

            # Validate date
            if apod_date < start_date:
                print(f"Date should not be before the date of the first APOD (i.e., 1995-06-16)")
                sys.exit()
            elif apod_date > date.today():
                print("Date should not be a date in the future (i.e., after today's date).")
                sys.exit()
        except ValueError:
            print("Invalid Date.")
            sys.exit()
    else:
        apod_date = date.today()
    return apod_date

def init_apod_cache():
    """Initializes the image cache by:
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    """
    # TODO: Create the image cache directory if it does not already exist
    if os.path.exists(image_cache_dir):
            print("Image Cache already exists")
    else:
        os.mkdir(image_cache_dir)
        print("Image cache directory created.")
    
    # TODO: Create the DB if it does not already exist
    if os.path.exists(image_cache_db):
        print("DB already exists")
    else:
        con = sqlite3.connect(image_cache_db)
        print("Image cache DB created.")
    return

def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """
    print("APOD date:", apod_date.isoformat())
    # TODO: Download the APOD information from the NASA API
    # Hint: Use a function from apod_api.py 
    apod_info = apod_api.get_apod_info(apod_date)
    try:
        url = apod_info['thumbnail_url']
    except:
        url = apod_info['url']
    
    if url == "":
        print("No image url in apod")
        sys.exit()


    print(f"APOD title: {apod_info['title']}")
    print(f"APOD URL: {url}")

    # TODO: Download the APOD image
    # Hint: Use a function from image_lib.py 
    print("Downloading image from")
    image = image_lib.download_image(url)
    image_sha = hashlib.sha256(image).hexdigest()
    print(f"APOD SHA-256: {image_sha}")
    # TODO: Check whether the APOD already exists in the image cache
    # Hint: Use the get_apod_id_from_db() function below
    # TODO: Complete function body
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    create_records_tbl_query = """
        CREATE TABLE IF NOT EXISTS Records
        (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            explanation TEXT NOT NULL,
            file_path TEXT NOT NULL,
            sha256 TEXT NOT NULL
        );
    """
    cur.execute(create_records_tbl_query)
    apod_exists = get_apod_id_from_db(image_sha)
    if apod_exists == 0:
        # TODO: Save the APOD file to the image cache directory
        # Hint: Use the determine_apod_file_path() function below to determine the image file path
        # Hint: Use a function from image_lib.py to save the image file
        print("APOD image is not already in cache.")
        image_path = determine_apod_file_path(apod_info['title'], url)
        print("APOD file path: {image_path}")
        image_lib.save_image_file(image, image_path)

        # TODO: Add the APOD information to the DB
        # Hint: Use the add_apod_to_db() function below
        id = add_apod_to_db(apod_info['title'], apod_info['explanation'], image_path, image_sha)
        return id 
    else:
        print("APOD image is already in cache.")
        return apod_exists

def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful. Zero, if unsuccessful       
    """
    try:
        con = sqlite3.connect(image_cache_db)
        cur = con.cursor()
        add_record_query = """
            INSERT INTO Records
            (
                title,
                explanation,
                file_path,
                sha256
                )
                VALUES (?, ?, ?, ?);
            """
        
        new_record = (
            title,
            explanation,
            file_path,
            sha256
        ) 
        cur.execute(add_record_query, new_record)
        con.commit()    
        print("Adding APOD to image cache DB...success")
        return cur.lastrowid
    except:
        return 0
    
def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    # TODO: Complete function body
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    query = "SELECT id FROM Records WHERE sha256 = ?"
    cur.execute(query, (image_sha256,))
    selected = cur.fetchall()
    if len(selected) == 1:
        return selected[0][0]
    else:
        return 0

def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    # TODO: Complete function body
    # Hint: Use regex and/or str class methods to determine the filename.
    extension = image_url.split('.')[-1]
    cleaned_title = re.sub(r'\W+', '_', image_title.strip())
    path = f'{image_cache_dir}\\{cleaned_title}.{extension}'
    return path

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    # TODO: Query DB for image info
    # TODO: Put information into a dictionary
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    query = "SELECT title, explanation, file_path FROM Records WHERE id = ?"
    cur.execute(query, (image_id,))
    result = cur.fetchone()
    return {'title' : result[0], 'explantion': result[1], 'file_path': result[2]}

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """
    # TODO: Complete function body
    # NOTE: This function is only needed to support the APOD viewer GUI
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    cur.execute("SELECT title FROM Records")
    selected = cur.fetchall()
    new_tuple = tuple(item[0] for item in selected)
    return new_tuple

def get_apod_info_from_title(image_title):
    """Gets the title, explanation, and full path of the APOD having a specified
    title from the DB.

    Args:
        image_title (sript): title of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    # TODO: Query DB for image info
    # TODO: Put information into a dictionary
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    query = "SELECT title, explanation, file_path FROM Records WHERE title = ?"
    cur.execute(query, (image_title,))
    result = cur.fetchone()
    return {'title' : result[0], 'explantion': result[1], 'file_path': result[2]}


if __name__ == '__main__':
    main()