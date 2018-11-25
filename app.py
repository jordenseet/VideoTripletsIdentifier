from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os.path
import requests, os
import cv2
import numpy as np
import json

app = Flask(__name__)
app.config.from_pyfile('config.py')

for folder in (app.config['IMAGE_UPLOAD_FOLDER'], app.config['VIDEO_UPLOAD_FOLDER'], app.config['KEYFRAME_UPLOAD_FOLDER']):
    if not os.path.isdir(folder):
        print(f'Created {folder}')
        os.mkdir(folder)


@app.route('/', methods=['GET', 'POST'])
def index():
    directory_name = None
    if request.method == "POST":
        print(request.files)
        if 'file' in request.files:  # videos and images both appear as 'file'
            file = request.files['file']  # gets the file
            if file.filename != '':
                extension = file.filename.split(".")[-1]  # gets the extension of the file
                if extension in app.config['ALLOWED_IMAGE_EXTENSIONS']:  # checks if the extension is an image allowed extension
                    directory_name = app.config['IMAGE_UPLOAD_FOLDER']
                elif extension in app.config['ALLOWED_VIDEO_EXTENSIONS']:  # checks if the extension is a video allowed extension
                    directory_name = app.config['VIDEO_UPLOAD_FOLDER']

                if directory_name:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(directory_name, filename))
    
    uploaded_files = []
    # adds all file names and the file types to a tuple array
    uploaded_files.extend((video, app.config['VIDEO_UPLOAD_FOLDER'][2:]) for video in os.listdir(app.config['VIDEO_UPLOAD_FOLDER']))
    uploaded_files.extend((video, app.config['IMAGE_UPLOAD_FOLDER'][2:]) for video in os.listdir(app.config['IMAGE_UPLOAD_FOLDER']))
    keyframes = [(video, app.config['KEYFRAME_UPLOAD_FOLDER'][2:]) for video in os.listdir(app.config['KEYFRAME_UPLOAD_FOLDER'])]

    # print(uploaded_files)
    uploaded_files = tuple(uploaded_files)  # casts the list to tuple
    return render_template('index.html', uploaded_files=uploaded_files, keyframes=keyframes)


@app.route('/<filetype>/<filename>')
def uploaded_file(filetype, filename):
    folder = app.config["IMAGE_UPLOAD_FOLDER"] if filetype.lower() == "images" \
        else app.config["VIDEO_UPLOAD_FOLDER"] if filetype.lower() == "videos" \
        else app.config["KEYFRAME_UPLOAD_FOLDER"]
    return send_from_directory(folder, filename)


@app.route('/<filetype>/<filename>/delete')
def delete_file(filetype, filename):
    folder = app.config["IMAGE_UPLOAD_FOLDER"] if filetype.lower() == "images" \
    	else app.config["VIDEO_UPLOAD_FOLDER"] if filetype.lower() == "videos" \
    	else app.config["KEYFRAME_UPLOAD_FOLDER"]
    filepath = os.path.join(folder, filename)
    if os.path.isfile(filepath):
        os.remove(filepath)

    return redirect(url_for('index'))


@app.route('/<folder>/get_image_captions', methods=['GET'])
def get_image_captions(folder):
    # Set image_path to the local path of an image that you want to analyze.
    filename = request.args['file'] if 'file' in request.args else ''
    image_path = os.path.join(folder, filename)

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
    response   = requests.post(app.config['AZURE_VISION_ANALYZE_URL'], 
                 headers=headers, params=params, data=image_data)
    response.raise_for_status()

    # The 'analysis' object contains various fields that describe the image. The most
    # relevant caption for the image is obtained from the 'description' property.
    analysis = response.json()
    print(analysis)
    image_caption = analysis["description"]["captions"][0]["text"].capitalize()
    image_triplets = triplets(image_caption)
    return json.dumps({ 'caption': image_caption, 'triplet': json.loads(image_triplets) })


@app.route('/upload_video_to_azure', methods=['GET'])
def upload_video_to_azure():
    # Set video_path to the local path of a video that you want to analyze.
    filename   = request.args['file'] if 'file' in request.args else ''
    token      = get_account_access_token()
    params     = {'accessToken': token, 'name': filename}
    headers    = {'Content-Type': 'multipart/form-data'}
    video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], filename)
    files      = {'file' : open(video_path, 'rb').read()}
    response   = requests.post(app.config['VIDEO_INDEXER_VIDEO_UPLOAD_URL'],
                 params=params, headers=headers, files=files)
    response.raise_for_status()
    result = response.json()
    return result


@app.route('/chunking', methods=['GET'])
def chunking():
    folder = app.config['KEYFRAME_UPLOAD_FOLDER'][2:]  
    filename   = request.args['file'] if 'file' in request.args else ''
    filename_wo_ext = filename.split(".")[0]
    video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], filename)
    vidcap = cv2.VideoCapture(video_path)
    count = 0
    prev_image = None

    while True:
        # set time in video to capture
        vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*1000)) 
        success, image = vidcap.read()
        if not success:
            break
            
        # save frame as JPEG file
        # cv2.imwrite(os.path.join(folder,"frame{:d}.jpg".format(count)), image)     
        # comparing between 2 images
        if not prev_image is None:

            # accumulator variables to calculate similarity
            dot_product = 0
            magnitude_a = 0
            magnitude_b = 0
            for row in range(len(image)):
                for col in range(len(image[0])):
                    rgb          = image[row][col]
                    prev_rgb     = prev_image[row][col]
                    grey         = int(0.3*rgb[0] + 0.59*rgb[1] + 0.11*rgb[2])
                    prev_grey    = int(0.3*prev_rgb[0] + 0.59*prev_rgb[1] + 0.11*prev_rgb[2])
                    dot_product += grey*prev_grey
                    magnitude_a += grey**2
                    magnitude_b += prev_grey**2
                    
            similarity = 0
            try:
                similarity = dot_product / (magnitude_a**0.5 * magnitude_b**0.5)
                if similarity < 0.93:
                    cv2.imwrite(os.path.join(folder,"frame{:d}.jpg".format(count)), image)
            except Exception as e:
                pass
                
            print(similarity)
            
        prev_image = image
        count += 1
    return "Success"


@app.route('/triplets/<text>', methods=['GET'])
def triplets(text):
    if text != '':
        response = requests.get(f"http://www.newventify.com/rdf?sentence={text}")
        triples = response.json()
        result = { word: triples[word]['word'] for word in ['object', 'subject', 'predicate'] }
        return json.dumps(result)
    return ''

def get_account_access_token():
    subscription_key = app.config['VIDEO_INDEXER_SUBSCRIPTION_KEY']
    location         = app.config['VIDEO_INDEXER_LOCATION']
    accountId        = app.config['VIDEO_INDEXER_ACCOUNT_ID']
    
    headers    = {'Ocp-Apim-Subscription-Key': subscription_key}
    params     = {'allowEdit': 'true'}
    response   = requests.get(app.config['VIDEO_INDEXER_ACCOUNT_AUTH_URL'], headers=headers, params=params)
    response.raise_for_status()
    token = response.json()
    return token


if __name__ == "__main__":
    app.run(debug=True)