'''
Authors: Mahenur Master, Nisharg Patel, Sneha Malhotra , Siddharth Patel
Library of useful functions for working with images.
'''

import requests
import ctypes
import os
from ctypes import wintypes

def main():
    # Test the functions in this module
    test_image_url = "https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg"
    image_data = download_image(test_image_url)
    if image_data:
        image_path = os.path.join(os.getcwd(), "test_image.jpg")
        if save_image_file(image_data, image_path):
            set_desktop_background_image(image_path)

def download_image(image_url):
    """Downloads an image from a specified URL.

    DOES NOT SAVE THE IMAGE FILE TO DISK.

    Args:
        image_url (str): URL of image

    Returns:
        bytes: Binary image data, if successful. None, if unsuccessful.
    """
    try:
        print(f"Downloading image from {image_url}...")
        response = requests.get(image_url)
        response.raise_for_status()
        print("Download successful.")
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return None

def save_image_file(image_data, image_path):
    """Saves image data as a file on disk.
    
    DOES NOT DOWNLOAD THE IMAGE.

    Args:
        image_data (bytes): Binary image data
        image_path (str): Path to save image file

    Returns:
        bool: True, if successful. False, if unsuccessful
    """
    try:
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        with open(image_path, 'wb') as file:
            file.write(image_data)
        print(f"Image saved to {image_path}.")
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False

def set_desktop_background_image(image_path):
    """Sets the desktop background image to a specific image.

    Args:
        image_path (str): Path of image file

    Returns:
        bool: True, if successful. False, if unsuccessful        
    """
    try:
        print(f"Setting desktop background to {image_path}...")
        SPI_SETDESKWALLPAPER = 20
        result = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER, 0, image_path, 3
        )
        if result:
            print("Desktop background set successfully.")
            return True
        else:
            print("Failed to set desktop background.")
            return False
    except Exception as e:
        print(f"Error setting desktop background: {e}")
        return False

def scale_image(image_size, max_size=(800, 600)):
    """Calculates the dimensions of an image scaled to a maximum width
    and/or height while maintaining the aspect ratio  

    Args:
        image_size (tuple[int, int]): Original image size in pixels (width, height) 
        max_size (tuple[int, int], optional): Maximum image size in pixels (width, height). Defaults to (800, 600).

    Returns:
        tuple[int, int]: Scaled image size in pixels (width, height)
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    # NOTE: This function is only needed to support the APOD viewer GUI
    resize_ratio = min(max_size[0] / image_size[0], max_size[1] / image_size[1])
    new_size = (int(image_size[0] * resize_ratio), int(image_size[1] * resize_ratio))
    return new_size

if __name__ == '__main__':
    main()
