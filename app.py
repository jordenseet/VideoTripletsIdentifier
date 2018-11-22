from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os.path
import requests, os

app = Flask(__name__)
app.config.from_pyfile('config.py')

if not os.path.isdir(app.config['IMAGE_UPLOAD_FOLDER']):
    print(f'Created {app.config["IMAGE_UPLOAD_FOLDER"]}')
    os.mkdir(app.config['IMAGE_UPLOAD_FOLDER'])

if not os.path.isdir(app.config['VIDEO_UPLOAD_FOLDER']):
    print(f'Created {app.config["VIDEO_UPLOAD_FOLDER"]}')
    os.mkdir(app.config['VIDEO_UPLOAD_FOLDER'])


@app.route('/', methods=['GET', 'POST'])
def index():
    directory_name = None
    if request.method == "POST":
        print(request.files)
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                extension = file.filename.split(".")[-1]
                if extension in app.config['ALLOWED_IMAGE_EXTENSIONS']:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
                    directory_name = (app.config['IMAGE_UPLOAD_FOLDER'])
                    # return redirect(url_for('uploaded_file', filename=filename))
                elif extension in app.config['ALLOWED_VIDEO_EXTENSIONS']:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], filename))
                    directory_name = (app.config['VIDEO_UPLOAD_FOLDER'])
    
    uploaded_files = []
    for video in os.listdir(app.config['VIDEO_UPLOAD_FOLDER']):
        uploaded_files.append(tuple([video,app.config['VIDEO_UPLOAD_FOLDER'][2:]]))
    for image in os.listdir(app.config['IMAGE_UPLOAD_FOLDER']):
        uploaded_files.append(tuple([image,app.config['IMAGE_UPLOAD_FOLDER'][2:]]))

    print(uploaded_files)
    uploaded_files = tuple(uploaded_files)
    return render_template('index.html', uploaded_files=uploaded_files)


@app.route('/images/<filename>')
def uploaded_image_file(filename):
    return send_from_directory(app.config['IMAGE_UPLOAD_FOLDER'], filename)

@app.route('/videos/<filename>')
def uploaded_video_file(filename):
    return send_from_directory(app.config['VIDEO_UPLOAD_FOLDER'], filename)


@app.route('/images/<filename>/delete')
def delete_video_file(filename):
    image_path = os.path.join(app.config["IMAGE_UPLOAD_FOLDER"], filename)
    if os.path.isfile(image_path):
        os.remove(image_path)

    return redirect(url_for('index'))

@app.route('/videos/<filename>/delete')
def delete_image_file(filename):
    video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], filename)
    if os.path.isfile(video_path):
        os.remove(video_path)

    return redirect(url_for('index'))


@app.route('/azure', methods=['GET'])
def get_captions():
    # Set image_path to the local path of an image that you want to analyze.
    filename = request.args['file'] if 'file' in request.args else ''
    image_path = os.path.join(app.config["IMAGE_UPLOAD_FOLDER"], filename)

    # ensure that the file exists before we process it
    if not os.path.isfile(image_path):
        return redirect(url_for('index'))
    
    # Replace <Subscription Key> with your valid subscription key.
    subscription_key = app.config['OCP_APIM_SUBSCRIPTION_KEY']
    assert subscription_key

    # Read the image into a byte array
    image_data = open(image_path, "rb").read()
    headers    = {'Ocp-Apim-Subscription-Key': subscription_key,
                  'Content-Type': 'application/octet-stream'}
    params     = {'visualFeatures': 'Categories,Description,Color'}
    response = requests.post(
        app.config['AZURE_VISION_ANALYZE_URL'], headers=headers, params=params, data=image_data)
    response.raise_for_status()

    # The 'analysis' object contains various fields that describe the image. The most
    # relevant caption for the image is obtained from the 'description' property.
    analysis = response.json()
    print(analysis)
    image_caption = analysis["description"]["captions"][0]["text"].capitalize()
    return image_caption
    

if __name__ == "__main__":
    app.run(debug=True)