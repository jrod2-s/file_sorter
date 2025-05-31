import os

from datetime import datetime
from flask import Flask, request, send_file, render_template
from PIL import Image
from werkzeug.utils import secure_filename
from pymediainfo import MediaInfo

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/organize', methods=['POST'])
def organize():
    #TODO: 
    # Create a function that goes through all the files
    # If it is a JPEG, PNG, TIFF, RAW, MP4, MOV, etc, obtain internal timestamp
    # If it is any other file, get the timestamp given to it by the filesystem
    if 'image' not in request.files:
        return "No file part", 400
    
    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400
    if file and file.filename.lower().endswith(('.jpg', '.jpeg')):
        filename = secure_filename(file.filename)
        date_filename = jpg_time_stamp(filename)

        jpg_path = os.path.join(UPLOAD_FOLDER, date_filename)
        file.save(jpg_path)

        return send_file(jpg_path, as_attachment=True)

    return "Invalid file type. Please upload a JPEG.", 400

def jpg_time_stamp(file):
    """ Function to obtain timestamp for the JPG. """
    image = Image.open(file)
    exif_data = image._getexif()

    if 306 in exif_data:
        datetime_obj = datetime.strptime(exif_data[306], "%Y:%m:%d %H:%M:%S")
        file_time = datetime_obj.strftime("%Y_%m_%d_%H_%M_%S")

        file_name = file_time + "_" + file

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

    file_name = file_time + "_" + file

    return file_name

def mp4_time_stamp(file):
    """ Class to obtain timestamp for the MP4. """
    media_info = MediaInfo.parse(file)

    for track in media_info.tracks:
        if track.track_type == "General":
            time_metadata = track.encoded_date

            datetime_obj = datetime.strptime(time_metadata, "%Y-%m-%d %H:%M:%S %Z")
            
            file_time = datetime_obj.strftime("%Y_%m_%d_%H_%M_%S")

            file_name = file_time + "_" + file

            return file_name

        else:
            return None
        
def filesystem_time_stamp(file):
    """ Function that obtains timestamp from file system. """
    
    file_timestamp = os.path.getctime(file)
    
    datetime_obj = datetime.fromtimestamp(file_timestamp)

    file_time = datetime_obj.strftime("%Y_%m_%d_%H_%M_%S")

    file_name = file_time + "_" + file

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


if __name__ == '__main__':
    app.run(debug=True)
    print(jpg_time_stamp('bros.jpg'))

    print(png_time_stamp("scar.png"))

    print(mp4_time_stamp("rocket.mp4"))

    print(already_time_stamped("2023_12_06_22_56_34_bros"))

    print(filesystem_time_stamp("scar.png"))
