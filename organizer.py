import os
import json
from zipfile import ZipFile

from flask import Flask, request, send_file, render_template, abort
from werkzeug.utils import secure_filename

from timestamp import *
from utilities import *

#TODO: fix bug where html hardcoded file name is used
#TODO: Test website to see if it works with different time zones (make compatible with different timezones)
#TODO: Remove personal email and add email message submission

# Start Flask and Create Uploads Folder
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'

# Start the front end
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/tips')
def tips():
    return render_template("tips.html")

@app.route('/contact')
def contact():
    return render_template('contact.html')


#Start the Backend
@app.route('/organize', methods=['POST'])
def organize():
    # Make upload folder
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    delete_zip()
    
    # Obtain data from user
    files = request.files.getlist('files')
    data = request.form.getlist('metadata')

    paths = []

    print(files)

    for file, metadata in zip(files, data):
        dictionary = json.loads(metadata)
        # print(dictionary)
        file_path = dictionary["relativePath"]
        timestamp = dictionary["lastModified"]
        print(f"timestamp: {timestamp}")

        print(f"filepath: {file_path}")

        file_path = os.path.normpath(file_path)

        print(f"normfilepath: {file_path}")

        parts = file_path.split(os.path.sep)
        safe_parts = [secure_filename(part) for part in parts]

        # Recombine into a safe relative path
        safe_path = os.path.join(*safe_parts)

        print(f"safepath: {safe_path}")

        full_path = os.path.join(UPLOAD_FOLDER, safe_path)
        file_name = os.path.basename(full_path)

        print(f"full_path: {full_path}")
        print(f"file_name: {file_name}")

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        file.save(full_path)
        print("Saved")

        # Set file name output value to none
        date_filename = None

       # Check if file already has timestamp
        if already_time_stamped(file_name):
            paths.append(full_path)
            continue
        # Timestamp a jpg
        elif file_name.lower().endswith(('.jpg', '.jpeg')): 
            date_filename = jpg_time_stamp(full_path)
        # Timestamp a png
        elif file_name.lower().endswith(('.png')):
            date_filename = png_time_stamp(full_path)
        # Timestamp a mp4
        elif file_name.lower().endswith(('.mp4')):
            date_filename = mp4_time_stamp(full_path)
        # Timestamp other files with filesystem time
        else: 
            date_filename = from_timestamp(full_path, timestamp)
        
        # If any of the special files cannot locate a timestamp, use filesystem time
        if date_filename is None:
            date_filename = from_timestamp(full_path, timestamp)

        rel_path = os.path.dirname(full_path)
        print(f"relpath: {rel_path}")

        # change file path name
        stamped_path = os.path.join(rel_path, date_filename).replace(os.sep, "/")
        print(f"Stampedpath: {stamped_path}")
        
        # Rename the file in extracted subfolder to new name
        stamped_path = unique_filename(stamped_path)
        os.rename(full_path, stamped_path)

        paths.append(stamped_path)
        print(f"relpath: {rel_path}")

    zip_path = rel_path.split(os.path.sep)[-1] + ".zip"
    print(f"zippath: {zip_path}")
    # convert uploaded folder to zip
    zip_folder(rel_path, zip_path)


    delete_uploads(UPLOAD_FOLDER)

    if os.path.exists(zip_path):
        return send_file(os.path.abspath(zip_path), as_attachment=True)
    
    else:
        return "File not found", 404



#TODO: 
    # Create a function that goes through all the files
    # If it is a JPEG, PNG, TIFF, RAW, MP4, MOV, etc, obtain internal timestamp
    # If it is any other file, get the timestamp given to it by the filesystem

if __name__ == '__main__':
    app.run(debug=True)