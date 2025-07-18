import os

from flask import Flask, request, send_file, render_template, abort
from werkzeug.utils import secure_filename

from timestamp import *
from utilities import *

#TODO: Figure out why time stamp is not being saved when uploading ...
# The array return nothing, reference test code
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
    # clean up random zip files
    # delete_zip()
    
    # Obtain zip file from user
    files = request.files.getlist('files')
    metadata = request.form.getlist('metadata')
    print("Flask")
    print(metadata)


    for file in files:
        file_path = file.filename
        file_path = os.path.normpath(file_path)


        return "done"

        parts = file_path.split(os.path.sep)
        safe_parts = [secure_filename(part) for part in parts]

        # Recombine into a safe relative path
        safe_path = os.path.join(*safe_parts)

        full_path = os.path.join(UPLOAD_FOLDER, safe_path)
        file_name = os.path.basename(full_path)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        file.save(full_path)

        paths = []

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

        path = os.path.dirname(full_path)

        # change file path name
        stamped_path = os.path.join(path, date_filename).replace(os.sep, "/")
        print(stamped_path)
        
        # Rename the file in extracted subfolder to new name
        stamped_path = unique_filename(stamped_path)
        os.rename(full_path, stamped_path)

        paths.append(stamped_path)

    # # Zip up the files
    # stamped_file_name = f"stamped_{zipfile}"

    # with ZipFile(stamped_file_name, "w") as zip:
    #     for file in paths:
    #         zip.write(file)

    # # Delete the uploads folder
    # delete_uploads(UPLOAD_FOLDER)

    return send_file(stamped_file_name, as_attachment=True)



#TODO: 
    # Create a function that goes through all the files
    # If it is a JPEG, PNG, TIFF, RAW, MP4, MOV, etc, obtain internal timestamp
    # If it is any other file, get the timestamp given to it by the filesystem

if __name__ == '__main__':
    app.run(debug=True)