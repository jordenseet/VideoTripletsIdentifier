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
    
    if not prev_image is None:
        total_similarity = 0
        row_length = len(image)
        col_length = len(image[0])
        for row in range(row_length):
            for col in range(col_length):
                rgb = image[row][col]
                prev_rgb = prev_image[row][col]
                dot_product = int(rgb[0])*int(prev_rgb[0]) + int(rgb[1])*int(prev_rgb[1]) + int(rgb[2])*int(prev_rgb[2])
                magnitude_a = (rgb[0]**2 + rgb[1]**2 + rgb[2]**2) ** 0.5
                magnitude_b = (prev_rgb[0]**2 + prev_rgb[1]**2 + prev_rgb[2]**2) ** 0.5
                
                cos_similarity = dot_product / (magnitude_a * magnitude_b) if magnitude_a != 0 and magnitude_b !=0 else 0
                total_similarity += cos_similarity 
            
        total_similarity /= (row_length * col_length)
        print(total_similarity)

    prev_image = image
    count += 1