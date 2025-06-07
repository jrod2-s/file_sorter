import os
from zipfile import ZipFile

from datetime import datetime
from flask import Flask, request, send_file, render_template
from PIL import Image
from werkzeug.utils import secure_filename
from pymediainfo import MediaInfo

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/organize', methods=['POST'])
def organize():
    if 'image' not in request.files:
        return "No file part", 400
    
    files = request.files.getlist('image')

    # Fix this line to ensure something is inputted
    if files == []:
        return "No selected file", 400
    
    paths = []
    
    for file in files:
    
        #TODO: Figure out why only one file was downloaded, and why it had a double time stamp
        # issue is parsing file path
        parts = os.path.normpath(file.filename).split(os.sep)
        safe_parts = [secure_filename(part) for part in parts if part not in ('', '.', '..')]

        secure_file_path = os.path.join(*safe_parts)
        secure_file_path = secure_file_path.replace(os.sep, "/")

        secure_file_name = os.path.basename(secure_file_path)

        if secure_file_path:
            date_filename = None

            if already_time_stamped(secure_file_name):

                date_filename = secure_file_name

            elif secure_file_path.lower().endswith(('.jpg', '.jpeg')):
                
                date_filename = jpg_time_stamp(secure_file_path)
            
            elif secure_file_path.lower().endswith(('.png')):

                date_filename = png_time_stamp(secure_file_path)

            elif secure_file_path.lower().endswith(('.mp4')):

                date_filename = mp4_time_stamp(secure_file_path)

            else: 
                date_filename = filesystem_time_stamp(secure_file_path)
            
            if date_filename is None:
                date_filename = filesystem_time_stamp(secure_file_path)

            jpg_path = os.path.join(UPLOAD_FOLDER, date_filename)
            jpg_path = jpg_path.replace(os.sep,"/")
            paths.append(jpg_path)
            file.save(jpg_path)

    with ZipFile("picture.zip", "w") as zip:
        for file in paths:
            zip.write(file)

    return send_file("picture.zip", as_attachment=True)

def jpg_time_stamp(file):
    """ Function to obtain timestamp for the JPG. """
    image = Image.open(file)
    exif_data = image._getexif()

    if 306 in exif_data:
        datetime_obj = datetime.strptime(exif_data[306], "%Y:%m:%d %H:%M:%S")
        file_time = datetime_obj.strftime("%Y_%m_%d_%H_%M_%S")

        file_name = file_time + "_" + os.path.basename(file)

        return file_name
    
    else:
        # Return None if there is no EXIF data
        return None

def png_time_stamp(file):
    """ Function to obtain timestamp for the PNG. """

    image = Image.open(file)

    if "Creation Time" in image.info:
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

def mp4_time_stamp(file):
    """ Class to obtain timestamp for the MP4. """
    media_info = MediaInfo.parse(file)

    for track in media_info.tracks:
        if track.track_type == "General":
            time_metadata = track.encoded_date

            datetime_obj = datetime.strptime(time_metadata, "%Y-%m-%d %H:%M:%S %Z")
            
            file_time = datetime_obj.strftime("%Y_%m_%d_%H_%M_%S")

            file_name = file_time + "_" + os.path.basename(file)

            return file_name

        else:
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
        datetime_obj = datetime.strptime(file_date, "%Y_%m_%d_%H_%M_%S")

        return True
    except:
        return False

def fix_time_stamp(file):
    """ Function that fixes the time stamp format. """
    pass



#TODO: Include other filetypes and fill in logic
# Maybe update functions to only output the date format and add the file name seperately
# Think of the issues that file paths will give you onve this is implemented

#TODO: 
    # Create a function that goes through all the files
    # If it is a JPEG, PNG, TIFF, RAW, MP4, MOV, etc, obtain internal timestamp
    # If it is any other file, get the timestamp given to it by the filesystem

if __name__ == '__main__':
    app.run(debug=True)
    # print(jpg_time_stamp('bros.jpg'))

    # print(png_time_stamp("scar.png"))

    # print(mp4_time_stamp("rocket.mp4"))

    # print(already_time_stamped("2023_12_06_22_56_34_bros"))

    # print(filesystem_time_stamp("scar.png"))
