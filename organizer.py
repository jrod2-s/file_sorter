import os
from abc import ABC, abstractmethod
import re

from datetime import datetime
from flask import Flask, request, send_file, render_template
from PIL import Image
from werkzeug.utils import secure_filename

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
        jpg_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(jpg_path)

        # Convert to PNG
        img = Image.open(jpg_path)
        png_filename = filename.rsplit('.', 1)[0] + '.png'
        png_path = os.path.join(CONVERTED_FOLDER, png_filename)
        img.save(png_path, 'PNG')

        return send_file(png_path, as_attachment=True)

    return "Invalid file type. Please upload a JPEG.", 400

class FileTimeStamp(ABC):
    """ Abstract Class to obtain timestamp. """
    @abstractmethod
    def timestamp(self, file):
        
        pass

class JPGTimeStamp(FileTimeStamp):
    """ Class to obtain timestamp for the JPG. """
    @abstractmethod
    def timestamp(self, file):
        image = Image.open(file)
        exif_data = image._getexif()

        time_list = re.split(r'[:,\s]+', exif_data[306])

        date = datetime(int(time_list[0]), int(time_list[1]),int(time_list[2]), int(time_list[3]), int(time_list[4]), int(time_list[5]))

        file_time = date.strftime("%Y_%m_%d_%H_%M_%S")

        file_name = file_time + file

class PNGTimeStamp(FileTimeStamp):
    """ Class to obtain timestamp for the PNG. """
    @abstractmethod
    def timestamp(self, file):
        pass

class MP4TimeStamp(FileTimeStamp):
    """ Class to obtain timestamp for the MP4. """
    @abstractmethod
    def timestamp(self, file):
        pass

#TODO: Include other filetypes and fill in logic


if __name__ == '__main__':
    app.run(debug=True)
