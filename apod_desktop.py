""" 
COMP 593 - Final Project

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
import image_lib
import inspect
import sys
import sqlite3
import apod_api
import re
import hashlib

# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

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
    today_date = date.today()
    first_apod = date(1995, 6, 16)
    if len(sys.argv)<2:
        apod_date = date.fromisoformat(str(today_date))
        return apod_date
    else:
        try:
            apod_date = date.fromisoformat(sys.argv[1])
            if apod_date > today_date:
                raise ArithmeticError('APOD date cannot be in the future')
            if apod_date < first_apod:
                raise ArithmeticError('APOD date cannot be before the date of the first APOD (i.e., 1995-06-16)')
        except ValueError as e:
            print('Error:Invalid date format;',e)
            print('Script execution aborted')
            sys.exit()
        except ArithmeticError as e:
            print('Error: ',e)
            print('Script execution aborted')
            sys.exit()
    return apod_date

def get_script_dir():
    """Determines the path of the directory in which this script resides

    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    return os.path.dirname(script_path)

def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.

    Args:
        parent_dir (str): Full path of parent directory    
    """
    global image_cache_dir
    global image_cache_db
    # TODO: Determine the path of the image cache directory
    image_cache_dir = os.path.join(parent_dir, "cache")
    print("Image cache directory: " + image_cache_dir)
    # TODO: Create the image cache directory if it does not already exist
    if not os.path.exists(image_cache_dir):
        os.makedirs(image_cache_dir)
        print("Image cache directory created: " + str(image_cache_dir))
    else:
        print('Image cache directory already exists.')
    # TODO: Determine the path of image cache DB
    image_cache_db = os.path.join(image_cache_dir, 'cache.db')
    print("Image cache DB path: " + image_cache_db)
    # TODO: Create the DB if it does not already exist
    with sqlite3.connect(image_cache_db) as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS apod_cache (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                  "title TEXT NOT NULL, explanation TEXT NOT NULL, image_path TEXT NOT NULL UNIQUE, "
                  "image_sha256 TEXT NOT NULL UNIQUE)")
        conn.commit()
        print("Image cache DB created: " + str(image_cache_db))


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
    apod_info_dict=apod_api.get_apod_info(apod_date)
    if apod_info_dict is None:
        sys.exit()
    title = apod_info_dict['title']
    print("APOD title: " + title)
    media_type = apod_info_dict['media_type']
    print('APOD media type'+ media_type)
    if media_type=='image':
        url = apod_info_dict['hdurl']
    elif media_type=='video':
        url=apod_info_dict['url']
    print("APOD URL : "+url)
    # TODO: Download the APOD image
    image_data = image_lib.download_image(url)
    # Compute the SHA-256 hash value of the image data
    sha256 = hashlib.sha256(image_data).hexdigest()
    print('APOD SHA-256:',sha256)
    # TODO: Check whether the APOD already exists in the image cache
    apod_id = get_apod_id_from_db(sha256)
    if apod_id:
        print('APOD image is already in cache.')
        return apod_id
    # TODO: Save the APOD file to the image cache directory
    print('APOD image is not already in cache.')
    image_path=determine_apod_file_path(title,url)
    print('APOD file path:',image_path)
    image_lib.save_image_file(image_data, image_path)
    # TODO: Add the APOD information to the DB
    explanation= apod_info_dict['explanation']
    record_id=add_apod_to_db(title,explanation,image_path,sha256)
    return record_id

def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful.  Zero, if unsuccessful       
    """
    # TODO: Complete function body
    print('Adding APOD to image cache DB...',end='')
    with sqlite3.connect(image_cache_db) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO apod_cache (title, explanation, image_path, image_sha256) VALUES (?, ?, ?, ?)",
                  (title, explanation, file_path, sha256))
        conn.commit()
        print('success')
        return c.lastrowid
    print('failure')
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
    with sqlite3.connect(image_cache_db) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM apod_cache WHERE image_sha256=?", (image_sha256,))
        row = c.fetchone()
        if row:
            return row[0]
        else:
            return 0
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
    file_name = re.sub(r"[^\w\s]", "", image_title).strip().replace(" ", "_")
    file_name = re.sub(r"\s+", "_", file_name)
    file_ext=image_url.split('.')[-1]
    image_path = os.path.join(image_cache_dir, f"{file_name}.{file_ext}")
    return image_path

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    # TODO: Query DB for image info
    with sqlite3.connect(image_cache_db) as conn:
        c = conn.cursor()
        c.execute("SELECT title, explanation, image_path FROM apod_cache WHERE id=?", (image_id,))

        row = c.fetchone()
        # TODO: Put information into a dictionary
        if row:
            apod_info = {
                'title': row[0],
                'explanation': row[1],
                'file_path': row[2],
            }
            return apod_info
        else:
            return None

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """
    # TODO: Complete function body
    # NOTE: This function is only needed to support the APOD viewer GUI
    with sqlite3.connect(image_cache_db) as conn:
        c = conn.cursor()
        c.execute("SELECT title FROM apod_cache")
        row = c.fetchall()

    return [r[0] for r in row]

if __name__ == '__main__':
    main()