import os

from flask import Flask, request, send_file, render_template, abort
from werkzeug.utils import secure_filename

from timestamp import *
from utilities import *

#TODO: Update website to explain that 7z zip files are better for maintaining the date
#TODO: Deploy this and figure out what else is needed along the way

# Start Flask and Create Uploads Folder
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'

# Start the front end
@app.route('/')
def index():
    return render_template('modern.html')


#Start the Backend
@app.route('/organize', methods=['POST'])
def organize():
    # Make upload folder
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # clean up random zip files
    delete_zip()
    
    # Obtain zip file from user
    file = request.files['file']
    zipfile = secure_filename(file.filename)

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
    else:
        raise Exception("Files extension is missing or not supported.")


    # Extract the zip file
    extracted_folder = zipfile[0:parse_val] + "_extracted"
    extracted_path = os.path.join(UPLOAD_FOLDER, extracted_folder).replace(os.sep, "/")

    if zip:
        secure_extract(zip_path, extracted_path)
    elif seven_z:
        secure_extract_7z(zip_path, extracted_path)

    # Obtain a list of all the files within the folder
    extracted_subfolder = zipfile[0:parse_val]

    subfolder_path = os.path.join(UPLOAD_FOLDER, extracted_folder, extracted_subfolder).replace(os.sep, "/")

    files = [f for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))]

    # Loop through the list and change the name of the file in that extracted folder
    paths = []

    for file in files:
        file_name = file
        file_path = os.path.join(subfolder_path, file).replace(os.sep, "/")

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

        # change file path name
        stamped_path = os.path.join(extracted_path, date_filename).replace(os.sep, "/")
        
        # Rename the file in extracted subfolder to new name
        stamped_path = unique_filename(stamped_path)
        os.rename(file_path, stamped_path)

        paths.append(stamped_path)

    # Zip up the files
    stamped_file_name = f"stamped_{zipfile}"

    with ZipFile(stamped_file_name, "w") as zip:
        for file in paths:
            zip.write(file)

    # Delete the uploads folder
    delete_uploads(UPLOAD_FOLDER)

    return send_file(stamped_file_name, as_attachment=True)



#TODO: 
    # Create a function that goes through all the files
    # If it is a JPEG, PNG, TIFF, RAW, MP4, MOV, etc, obtain internal timestamp
    # If it is any other file, get the timestamp given to it by the filesystem

if __name__ == '__main__':
    app.run(debug=True)