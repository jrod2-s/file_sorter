import os
import json
import logging
from zipfile import ZipFile

from flask import Flask, request, send_file, render_template, abort, Response
from werkzeug.utils import secure_filename

from timestamp import *
from utilities import *

#TODO: Test website to see if it works with different time zones (make compatible with different timezones)
#TODO: Include google drive, drop box and link submission
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

@app.route('/sitemap.xml')
def sitemap():
    xml =  render_template('sitemap.xml')
    return Response(xml, mimetype='application/xml')

#Start the Backend
@app.route('/organize', methods=['POST'])
def organize():
    try:
        # Start logger
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='filesorter.log')
        logger = logging.getLogger(__name__)
        logger.info("Logger started!")

        # Make upload folder and delete zip file made previously
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        delete_zip()
        
        # Obtain data from user
        files = request.files.getlist('files')
        data = request.form.getlist('metadata')

        paths = []

        # Loop through files and timestamp meta data
        for file, metadata in zip(files, data):
            dictionary = json.loads(metadata)
            file_path = dictionary["relativePath"]
            timestamp = dictionary["lastModified"]

            # Make the inputted path a safe file path
            file_path = os.path.normpath(file_path)

            parts = file_path.split(os.path.sep)
            safe_parts = [secure_filename(part) for part in parts]

            # Recombine into a safe relative path
            safe_path = os.path.join(*safe_parts)

            # Define new path under upload folder
            full_path = os.path.join(UPLOAD_FOLDER, safe_path)
            file_name = os.path.basename(full_path)

            # Create new file path directory
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Save uploaded files
            file.save(full_path)

            # Set file name output value to none
            date_filename = None

        # Check if file already has timestamp
            if already_time_stamped(file_name):
                logger.info(f"Already timestamped: {file_name}")
                paths.append(full_path)
                continue
            # Timestamp a jpg
            elif file_name.lower().endswith(('.jpg', '.jpeg')): 
                date_filename = jpg_time_stamp(full_path)
                logger.info(f"JPG datafile name: {date_filename}")
            # Timestamp a png
            elif file_name.lower().endswith(('.png')):
                date_filename = png_time_stamp(full_path)
                logger.info(f"PNG datafile name: {date_filename}")
            # Timestamp a mp4
            elif file_name.lower().endswith(('.mp4')):
                date_filename = mp4_time_stamp(full_path)
                logger.info(f"MP4 datafile name: {date_filename}")
            # Timestamp other files with filesystem time
            else: 
                date_filename = from_timestamp(full_path, timestamp)
            
            # If any of the special files cannot locate a timestamp, use filesystem time
            if date_filename is None:
                date_filename = from_timestamp(full_path, timestamp)

            logger.info(f"Final date filename: {date_filename}")

            rel_path = os.path.dirname(full_path)

            # change file path name
            stamped_path = os.path.join(rel_path, date_filename).replace(os.sep, "/")
            
            # Rename the file in extracted subfolder to new name
            stamped_path = unique_filename(stamped_path)
            os.rename(full_path, stamped_path)

            paths.append(stamped_path)

        zip_path = rel_path.split(os.path.sep)[-1] + ".zip"
        logger.info(zip_path)
        # convert uploaded folder to zip
        zip_folder(rel_path, zip_path)


        delete_uploads(UPLOAD_FOLDER)

        if os.path.exists(zip_path):
            return send_file(os.path.abspath(zip_path), as_attachment=True)
        
        else:
            logger.info("File not found.")
            return "File not found", 404
        
    except Exception as e:
        logger.info(e)

if __name__ == '__main__':
    app.run(debug=True)
