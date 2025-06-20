import os
import shutil
from zipfile import ZipFile
import tempfile

from datetime import datetime
from flask import Flask, request, send_file, render_template, abort
from PIL import Image
from werkzeug.utils import secure_filename
from pymediainfo import MediaInfo
import py7zr

#TODO: Figure out why the we are getting a file not found error 

# Start Flask and Create Uploads Folder
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# Start the front end
@app.route('/')
def index():
    return render_template('modern.html')


#Start the Backend
@app.route('/organize', methods=['POST'])
def organize():
    # Obtain zip file from user
    print("started")
    file = request.files['file']
    zipfile = secure_filename(file.filename)
    print("received file")

    # Check if file was inputted
    if zipfile == "":
        #TODO: Make simple text response not allowing you to not enter a file
        abort(404)

    # define booleans to note each file type
    zip = zipfile.lower().endswith((".zip"))
    seven_z = zipfile.lower().endswith((".7z"))

    if zip:
        parse_val = -4
    elif seven_z:
        parse_val = -3


    # Save off the zip file in the uploads folder
    if zip or seven_z:
        zip_path = os.path.join(UPLOAD_FOLDER, zipfile).replace(os.sep, "/")
        file.save(zip_path)
        print("saved file")
    else:
        raise Exception("Files extension is missing or not supported.")


    # Extract the zip file
    extracted_folder = zipfile[0:parse_val] + "_extracted"
    extracted_path = os.path.join(UPLOAD_FOLDER, extracted_folder).replace(os.sep, "/")

    if zip:
        secure_extract(zip_path, extracted_path)
    elif seven_z:
        secure_extract_7z(zip_path, extracted_path)

    print("extracted file")

    # Obtain a list of all the files within the folder
    extracted_subfolder = zipfile[0:parse_val]

    subfolder_path = os.path.join(UPLOAD_FOLDER, extracted_folder, extracted_subfolder).replace(os.sep, "/")
    print(subfolder_path)

    files = [f for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))]
    print("got file list")
    # Loop through the list and change the name of the file in that extracted folder

    paths = []

    for file in files:
        file_name = file
        file_path = os.path.join(subfolder_path, file).replace(os.sep, "/")
        print(f"made filepath for {file}")
        # Set file name output value to none
        date_filename = None

       # Check if file already has timestamp
        if already_time_stamped(file_name):
            paths.append(file_path)
            continue

        # Timestamp a jpg
        elif file_name.lower().endswith(('.jpg', '.jpeg')): 
            date_filename = jpg_time_stamp(file_path)
        
        # Timestamp a png
        elif file_name.lower().endswith(('.png')):
            date_filename = png_time_stamp(file_path)

        # Timestamp a mp4
        elif file_name.lower().endswith(('.mp4')):
            date_filename = mp4_time_stamp(file_path)

        # Timestamp other files with filesystem time
        else: 
            date_filename = filesystem_time_stamp(file_path)
        
        # If any of the special files cannot locate a timestamp, use filesystem time
        if date_filename is None:
            date_filename = filesystem_time_stamp(file_path)
        print(f"got new name {date_filename}")
        # change file path name
        stamped_path = os.path.join(extracted_path, date_filename).replace(os.sep, "/")
        
        print(f"new stamped path {stamped_path}")
        # Rename the file in extracted subfolder to new name
        stamped_path = unique_filename(stamped_path)
        os.rename(file_path, stamped_path)

        paths.append(stamped_path)

    print("got all paths in list")
    # Zip up the files
    stamped_file_name = "stamped_files.zip"

    with ZipFile(stamped_file_name, "w") as zip:
        for file in paths:
            zip.write(file)
    print("created zip")

    # Delete the uploads folder
    delete_uploads(UPLOAD_FOLDER)
    print("deleted uploads folder")

    return send_file(stamped_file_name, as_attachment=True)



   
    
    # for file in files:
    #     # Check the parts of directory to ensure it is safe
    #     parts = os.path.normpath(file.filename).split(os.sep)
    #     safe_parts = [secure_filename(part) for part in parts if part not in ('', '.', '..')]

    #     secure_file_path = os.path.join(*safe_parts)
    #     secure_file_path = secure_file_path.replace(os.sep, "/")



    #     # save file in uploads folder
    #     file_path = os.path.join(UPLOAD_FOLDER, secure_file_path)
    #     file_path = file_path.replace(os.sep,"/")
    #     os.makedirs(os.path.dirname(file_path), exist_ok=True)
    #     file.save(file_path)

    #     file_name = os.path.basename(file_path)
    #     file_dir = os.path.dirname(file_path)

 

    #     # Add path to list of paths to zip
    #     paths.append(stamped_path)
    # #TODO: Find a way to name the outputted zipfile
    # # Maybe use a default name promoting the website

    # # Create a zip file


def is_within_directory(directory, target):
    """" Check if absolute path for two directories are the same. """
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)

    return os.path.commonpath([abs_directory]) == os.path.commonpath([abs_directory, abs_target])

def secure_extract(zip_file, extract_path):
    """ Function that ensure files in zip are not malicious. """
    with ZipFile(zip_file) as z:
        for member in z.namelist():
            member_path = os.path.join(extract_path, member)
            if not is_within_directory(extract_path, member_path):
                raise Exception("Attempted Path Traversal.")
        z.extractall(extract_path)

def secure_extract_7z(zip_file, extract_path):
    with py7zr.SevenZipFile(zip_file, mode='r') as z:
        for member in z.getnames():
            member_path = os.path.join(extract_path, member)
            if not is_within_directory(extract_path, member_path):
                raise Exception("Attempted Path Traversal.")
        z.extractall(path=extract_path)


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
    
    file_timestamp = os.path.getctime(file)
    
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

def fix_time_stamp(file):
    """ Function that fixes the time stamp format. """
    pass

def delete_uploads(folder):
    """ Funtion that deletes the upload folder. """
    if os.path.exists(folder):
        shutil.rmtree(folder)

def unique_filename(file_path):
    base, ext = os.path.splitext(file_path)
    counter = 1
    new_path = file_path    

    while os.path.exists(new_path):
        new_path = f"{base} ({counter}){ext}"
        counter +=1

    return new_path


#TODO: Include other filetypes and fill in logic
# Maybe update functions to only output the date format and add the file name seperately
# Think of the issues that file paths will give you onve this is implemented

#TODO: 
    # Create a function that goes through all the files
    # If it is a JPEG, PNG, TIFF, RAW, MP4, MOV, etc, obtain internal timestamp
    # If it is any other file, get the timestamp given to it by the filesystem

if __name__ == '__main__':
    app.run(debug=True)