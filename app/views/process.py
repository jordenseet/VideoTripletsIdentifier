import json
import os
import subprocess

import requests

import config
import cv2
from classifier import AccidentsClassifier
from flask import Blueprint
from flask import current_app as app
from flask import jsonify, redirect, request, url_for

from image_caption import *

mod = Blueprint('process', __name__)
x = AccidentsClassifier()

YOLO_FOLDER = './yolo'

@mod.route('/images/detect')
def yolo(filename=None):
    # Set image_path to the local path of an image that you want to analyze.
    filename = request.args['file'] if filename is None else filename
    image_path = os.path.join(config.KEYFRAME_UPLOAD_FOLDER, filename)

    # ensure that the file exists before we process it
    if not os.path.isfile(image_path):
        return redirect(url_for('index'))

    cwd = os.getcwd()
    os.chdir(YOLO_FOLDER)
    p = subprocess.Popen(["darknet.exe", "detect", "cfg/yolov3.cfg", "yolov3.weights", f"../{image_path}"],
                        shell=True,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    print('out', out)
    print('err', err)
    os.chdir(cwd)
    os.remove(image_path.replace('.jpg', '_output.jpg'))
    # os.rename(f"{YOLO_FOLDER}/predictions.jpg", image_path)
    os.rename(f"{YOLO_FOLDER}/predictions.jpg", image_path.replace('.jpg', '_output.jpg'))
    # hasAccident = x.detect_accident(image_path)
    # print(hasAccident)
    # if hasAccident:
    #     os.remove(image_path)
    #     return "True"
    # else:
    #     return "False"


@mod.route('/images/captionize')
def image_captionize(filename=None):
    filename = request.args['file'] if filename is None else filename
    image_path = os.path.join(config.KEYFRAME_UPLOAD_FOLDER, filename)
    if not os.path.isfile(image_path):
        return { 'status': False }
    print(captionize(image_path))
    return { 'status': captionize(image_path) }


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
def chunking(filename=None):
    # for img in os.listdir(app.config['KEYFRAME_UPLOAD_FOLDER']):
    #     img = os.path.join(app.config['KEYFRAME_UPLOAD_FOLDER'], img)
    #     if os.path.isfile(img):
    #         os.remove(img)

    # folder = app.config['KEYFRAME_UPLOAD_FOLDER']
    # filename = request.args['file'] if 'file' in request.args else filename
    # video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], filename)
    # vidcap = cv2.VideoCapture(video_path)
    # count = 0

    # print("Chunking in progress")
    # while True:
    #     # set time in video to capture
    #     vidcap.set(cv2.CAP_PROP_POS_MSEC, (count*1000))
    #     success, image = vidcap.read()
    #     if not success:
    #         break

    #     # write image into keyframe
    #     cv2.imwrite(os.path.join(folder,
    #                 "frame{:d}.jpg".format(count)), image)

    #     count += 1

    print("Chunking complete")

    # detect car accidents
    # keyframes = [(video, app.config['KEYFRAME_UPLOAD_FOLDER'].split('/')[-1])
    #              for video in os.listdir(app.config['KEYFRAME_UPLOAD_FOLDER'])]
    # keyframes = sorted(keyframes, key=lambda x: int(''.join([ch for ch in x[0].split('.')[0] if ch.isdigit()])))
    # for video, folder in keyframes:
    #     yolo(video)
    # print('Detection complete')

    result = captionize_batch()
    print(result)

    # keyframes = [(video, app.config['KEYFRAME_UPLOAD_FOLDER'].split('/')[-1])
    #              for video in os.listdir(app.config['KEYFRAME_UPLOAD_FOLDER'])]
    # keyframes = sorted(keyframes, key=lambda x: int(''.join([ch for ch in x[0].split('.')[0] if ch.isdigit()])))
    # keyframes_caption = {}
    # for video, folder in keyframes:
    #     caption = image_captionize(video)
    #     if caption['status']:
    #         print('New caption:', caption)
    #         keyframes_caption[video] = caption

    # with open(os.path.join(app.config['UPLOAD_FOLDER'], 'keyframes_caption.json'), 'w') as f:
    #     f.write(json.dumps(keyframes_caption))

    return redirect(url_for('index'))


@mod.route('/triplets/<text>', methods=['GET'])
def triplets(text):
    if text != '':
        resp = requests.get(f"http://www.newventify.com/rdf?sentence={text}")
        triples = resp.json()
        result = {word: triples[word]['word']
                  for word in ['object', 'subject', 'predicate']}
        return jsonify(result)
    return ''
