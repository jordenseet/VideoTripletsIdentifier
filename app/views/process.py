import os
import subprocess

import cv2
import numpy as np
import requests
from flask import Blueprint
from flask import current_app as app
from flask import jsonify, redirect, request, url_for

import config

mod = Blueprint('process', __name__)


@mod.route('/images/detect')
def yolo():
    # Set image_path to the local path of an image that you want to analyze.
    filename = request.args['file'] if 'file' in request.args else ''
    image_path = os.path.join(config.IMAGE_UPLOAD_FOLDER, filename)

    # ensure that the file exists before we process it
    if not os.path.isfile(image_path):
        return redirect(url_for('index'))

    owd = os.getcwd()
    os.chdir('./assets')
    os.chmod('./darknet', 755)
    image_path = os.path.join('..', image_path)
    p = subprocess.run(['./darknet',
                        'detect',
                        'cfg/yolov3.cfg',
                        'yolov3.weights',
                        image_path], stdout=subprocess.PIPE)
    os.chdir(owd)
    if p.returncode == 0:
        result = p.stdout.decode('utf-8')
        print(result)
        if os.path.isfile('./assets/predictions.jpg'):
            return '''
            <html><body><img src="/assets/predictions.jpg" /></body></html>
            '''
        else:
            return result
    else:
        return 'Error'


@mod.route('/<folder>/get_image_captions', methods=['GET'])
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
    headers = {'Ocp-Apim-Subscription-Key': subscription_key,
               'Content-Type': 'application/octet-stream'}
    params = {'visualFeatures': 'Categories,Description,Color'}
    response = requests.post(app.config['AZURE_VISION_ANALYZE_URL'], 
                             headers=headers, params=params, data=image_data)
    response.raise_for_status()

    # The 'analysis' object contains various fields that describe the image. The most
    # relevant caption for the image is obtained from the 'description' property.
    analysis = response.json()
    print(analysis)
    image_caption = analysis["description"]["captions"][0]["text"].capitalize()
    image_triplets = triplets(image_caption)
    return jsonify({
        'caption': image_caption,
        'triplet': image_triplets.json()
    })


@mod.route('/chunking', methods=['GET'])
def chunking():
    folder = app.config['KEYFRAME_UPLOAD_FOLDER'][2:]  
    filename = request.args['file'] if 'file' in request.args else ''
    video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], filename)
    vidcap = cv2.VideoCapture(video_path)
    count = 0

    prev_image_greyscale = None
    prev_image_magnitude = None
    while True:
        # set time in video to capture
        vidcap.set(cv2.CAP_PROP_POS_MSEC, (count*1000))
        success, image = vidcap.read()
        if not success:
            break

        # grayscale current image
        image_greyscale = np.inner(image, [.3, .59, .11]).astype(np.int64)
        magnitude = np.square(image_greyscale).sum()

        # comparing between 2 images
        if prev_image_greyscale is not None:
            similarity = 0
            try:
                # accumulator variables to calculate similarity
                dot_product = (image_greyscale * prev_image_greyscale).sum()
                similarity = np.divide(
                    dot_product,
                    (np.sqrt(magnitude) * np.sqrt(prev_image_magnitude)))

                if similarity < 0.93:
                    # save frame as JPEG file
                    cv2.imwrite(
                        os.path.join(folder,
                                     "frame{:d}.jpg".format(count)), image)
            except Exception:
                pass

            print(similarity)

        prev_image_greyscale = image_greyscale
        prev_image_magnitude = magnitude
        count += 1
    return "Success"


@mod.route('/triplets/<text>', methods=['GET'])
def triplets(text):
    if text != '':
        resp = requests.get(f"http://www.newventify.com/rdf?sentence={text}")
        triples = resp.json()
        result = {word: triples[word]['word']
                  for word in ['object', 'subject', 'predicate']}
        return jsonify(result)
    return ''
