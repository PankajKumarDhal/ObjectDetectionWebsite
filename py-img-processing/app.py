from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import io
from PIL import Image
import os


app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Hello, World!'

def process_image(image):
    # Example: Perform simple object detection (convert image to grayscale)
    image = np.array(image)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed_image = Image.fromarray(gray_image)
    return processed_image

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/fileUpload', methods=['POST'])
def file_upload():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file and allowed_file(file.filename):
        image_stream = io.BytesIO(file.read())
        image_stream.seek(0)
        try:
            image = Image.open(image_stream)
            processed_image = process_image(image)

            # Save the processed image to bytes
            img_byte_arr = io.BytesIO()
            processed_image.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            img_bytes = img_byte_arr.read()

            # Save the image bytes directly to the 'result' folder
            result_folder = 'result'
            os.makedirs(result_folder, exist_ok=True)
            saved_filename = file.filename
            saved_path = os.path.join(result_folder, saved_filename)
            with open(saved_path, 'wb') as f:
                f.write(img_bytes)

            return jsonify({'images': [{'filename': saved_filename, 'path': saved_path}]})
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return 'File type not allowed'

@app.route('/result/<path:filename>')
def get_result(filename):
    return send_from_directory('result', filename)

if __name__ == '__main__':
    app.run(debug=True)