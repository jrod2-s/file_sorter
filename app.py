from flask import Flask, request, send_file, render_template
from PIL import Image
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
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

if __name__ == '__main__':
    app.run(debug=True)
