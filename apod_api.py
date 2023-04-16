'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''
import requests
from datetime import date
import json
def main():
    # TODO: Add code to test the functions in this module
    get_apod_info(date.fromisoformat(str(date.today())))
    return

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """
    api_key = "hSbm1PwvCLB7WaYaHZDFaBzjvufhBJocMen01Yc5"
    url = f"https://api.nasa.gov/planetary/apod?date={apod_date}&api_key={api_key}"
    print("Getting {} APOD information from NASA ...".format(apod_date), end='')
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        apod_info_dict= json.loads(response.text)
        print('success')
        print(apod_info_dict)
        return apod_info_dict
    else:
        print('failure')
        print(f"Error: Unable to retrieve APOD info. Status code: {response.status_code}")
        return

def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API

    Returns:
        str: APOD image URL
    """
    media_type = apod_info_dict['media_type']
    if media_type == "image":
        return apod_info_dict['hdurl']
    elif media_type == "video":
        return apod_info_dict['thumbnail_url']
    return

if __name__ == '__main__':
    main()