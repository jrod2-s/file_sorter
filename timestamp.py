#!/usr/bin/env python3

"""
Functions for handling file time stamps
"""
import os
from datetime import datetime

from PIL import Image
from pymediainfo import MediaInfo


def jpg_time_stamp(file):
    """ Function to obtain timestamp for the JPG. """
    try:
        image = Image.open(file)
        exif_data = image._getexif()

        if exif_data is None:
            # No exif data
            return None
        
        elif 306 in exif_data:
            datetime_obj = datetime.strptime(exif_data[306], "%Y:%m:%d %H:%M:%S")
            file_time = datetime_obj.strftime("%Y_%m_%d_%H_%M_%S")

            file_name = file_time + "_" + os.path.basename(file)

            return file_name
    
        else:
            # Return None if there is no EXIF data
            return None
        
    except Exception as e:
        print(e)
        return None

def png_time_stamp(file):
    """ Function to obtain timestamp for the PNG. """
    try:
        image = Image.open(file)

        if image.info is None:
            return None
        elif "Creation Time" in image.info:
            exif_data = image.info['Creation Time']
        elif "timestamp" in image.info:
            exif_data = image.info['timestamp']
        elif "data" in image.info:
            exif_data = image.info['date']
        else:
            return None
        
        datetime_obj = datetime.strptime(exif_data, "%Y:%m:%d %H:%M:%S")
        file_time = datetime_obj.strftime("%Y_%m_%d_%H_%M_%S")

        file_name = file_time + "_" + os.path.basename(file)

        return file_name
    except Exception as e:
        print(e)
        return None

def mp4_time_stamp(file):
    """ Class to obtain timestamp for the MP4. """
    try:
        media_info = MediaInfo.parse(file)

        if media_info is None:
            return None

        for track in media_info.tracks:
            if track.track_type == "General":
                time_metadata = track.encoded_date

                datetime_obj = datetime.strptime(time_metadata, "%Y-%m-%d %H:%M:%S %Z")
                
                file_time = datetime_obj.strftime("%Y_%m_%d_%H_%M_%S")

                file_name = file_time + "_" + os.path.basename(file)

                return file_name

            else:
                return None
            
    except Exception as e:
        print(e)
        return None
        
def filesystem_time_stamp(file):
    """ Function that obtains timestamp from file system. """
    
    file_timestamp = os.path.getmtime(file)
    
    datetime_obj = datetime.fromtimestamp(file_timestamp)

    file_time = datetime_obj.strftime("%Y_%m_%d_%H_%M_%S")

    file_name = file_time + "_" + os.path.basename(file)

    return file_name

def already_time_stamped(file):
    """ Function that checks if tile already has timestamp format. """
    try:
        file_date = file[0:19]
        datetime.strptime(file_date, "%Y_%m_%d_%H_%M_%S")

        return True
    except:
        return False
    
def from_timestamp(file, timestamp):
    """Given a timestamp, add it to the name. """
    filename = os.path.basename(file)

    file_time = datetime.fromtimestamp(int(timestamp)/1000).strftime("%Y_%m_%d_%H_%M_%S")

    file_name = + file_time + "_" + filename 

    return file_name

def fix_time_stamp(file):
    """ Function that fixes the time stamp format. """
    pass