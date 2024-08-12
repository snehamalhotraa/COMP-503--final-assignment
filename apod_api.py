"""
Authors: Mahenur Master, Nisharg Patel, Sneha Malhotra , Siddharth Patel
Module for interacting with NASA's Astronomy Picture of the Day (APOD) API.
"""

import requests

APOD_API_URL = 'https://api.nasa.gov/planetary/apod'

def main():
    """Test functions in this module."""
    # Example test case
    apod_date = '2023-08-10'
    apod_info = fetch_apod_info(apod_date)
    if apod_info:
        image_url = extract_apod_image_url(apod_info)
        print(f"APOD image URL for {apod_date}: {image_url}")
    else:
        print(f"Failed to retrieve APOD information for {apod_date}")

def fetch_apod_info(apod_date):
    """Fetches data from NASA's APOD API for the given date.

    Args:
        apod_date (str): Date for the desired APOD, formatted as YYYY-MM-DD.

    Returns:
        dict: A dictionary containing APOD information if the request is successful.
              Returns None if the request fails.
    """
    print(f"Fetching APOD information for {apod_date} from NASA...", end='')
    params = {
        'date': apod_date,
        'thumbs': True,
        'api_key': 'zDGHiR6GROUp4lyM6MnPkBlYa3eFGgsUJerUaRtC'
    }
    
    response = requests.get(APOD_API_URL, params=params)
    
    if response.status_code == requests.codes.ok:
        print("Success")
        return response.json()
    else:
        print("Failed")
        print(f"Error code: {response.status_code} ({response.reason})")
        return None

def extract_apod_image_url(apod_info_dict):
    """Extracts the URL of the APOD image from the provided APOD information.

    Depending on the media type, either the high definition image URL or the video thumbnail URL is returned.

    Args:
        apod_info_dict (dict): A dictionary containing APOD information.

    Returns:
        str: The URL of the APOD image, or None if the media type is unsupported.
    """
    media_type = apod_info_dict.get('media_type', '')
    
    if media_type == 'image':
        return apod_info_dict.get('hdurl', '')
    elif media_type == 'video':
        return apod_info_dict.get('thumbnail_url', '')
    else:
        return None

if __name__ == '__main__':
    main()
