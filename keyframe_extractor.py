from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os.path
import requests, os
import cv2

app = Flask(__name__)
app.config.from_pyfile('config.py')

folder = 'keyframes'  
filename = 'video.mp4'
# filename   = request.args['file'] if 'file' in request.args else ''
video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], filename)
vidcap = cv2.VideoCapture(video_path)
count = 0
prev = None
while True:
    # set time in video to capture
    vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*1000)) 
    success,image = vidcap.read()
    if not success:
        break
        
    # save frame as JPEG file
    cv2.imwrite(os.path.join(folder,"frame{:d}.jpg".format(count)), image)     
    
    if not prev is None:
        abs_diff = cv2.absdiff(image, prev)
        total_diff = cv2.sumElems(abs_diff)
        print(total_diff)

    prev = image
    count += 1