from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os.path
import requests, os
import cv2
import numpy as np

app = Flask(__name__)
app.config.from_pyfile('config.py')

folder = 'keyframes'  
filename = 'video.mp4'
# filename   = request.args['file'] if 'file' in request.args else ''
video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], filename)
vidcap = cv2.VideoCapture(video_path)
count = 0
prev_image = None

while True:
    # set time in video to capture
    vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*1000)) 
    success,image = vidcap.read()
    if not success:
        break
        
    # save frame as JPEG file
    cv2.imwrite(os.path.join(folder,"frame{:d}.jpg".format(count)), image)     
    
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
            
        similarity = dot_product / (magnitude_a**0.5 * magnitude_b**0.5)
        print(similarity)

    prev_image = image
    count += 1