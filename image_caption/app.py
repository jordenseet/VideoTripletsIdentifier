import os
import sys
import subprocess

if len(sys.argv) == 1 or not os.path.isfile(sys.argv[1]):
        print('Usage: app.py <image_filepath>')
        exit()

import numpy as np
from pickle import load
# from numpy import argmax
# from keras.preprocessing.sequence import pad_sequences
from keras.applications.vgg16 import VGG16
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.models import Model
from keras.models import load_model
from utility import *

import tkinter as tk  
from PIL import Image, ImageTk

import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

dir_path = os.path.dirname(os.path.realpath(__file__))

# load the tokenizer
tokenizer = load(open(os.path.join(dir_path, 'tokenizer.pkl'), 'rb'))
# pre-define the max sequence length (from training)
max_length = 34


def extract_features(filename):
    vgg_model = VGG16()
    vgg_model.layers.pop()
    vgg_model = Model(inputs=vgg_model.inputs, outputs=vgg_model.layers[-1].output)

    image = load_img(filename, target_size=(224, 224))
    image = img_to_array(image)
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    image = preprocess_input(image)
    feature = vgg_model.predict(image, verbose=0)
    return feature


def captionize(photo):
    # load the model
    model = load_model(os.path.join(dir_path, 'model_19.h5'))
    features = extract_features(photo)
    return generate_desc(model, tokenizer, features, max_length)[len('startseq '):-len(' endseq')]


def show_output(image, caption="Result", triplets=''):
    root = tk.Tk()
    root.title(caption)
    root.geometry('660x550')
    im = Image.open(image)
    im = im.resize((640, 480), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(im)
    cv = tk.Canvas()
    cv.pack(side='top', fill='both', expand='yes')
    cv.create_image(10, 10, image=photo, anchor='nw')
    label = tk.Label(text=triplets, wraplength=480)
    label.pack(side='top')
    root.mainloop()


if __name__ == "__main__":
    # load and prepare the photograph
    # photo = extract_features(sys.argv[1])
    # generate description
    # description = generate_desc(model, tokenizer, photo, max_length)

    cwd = os.getcwd()
    image_path = os.path.realpath(sys.argv[1])
    
    # Step 1: Object Detection
    os.chdir('../yolo')
    if os.path.isfile('predictions.jpg'):
        print('Clearning previous session...')
        os.remove('predictions.jpg')
    p = subprocess.Popen(["darknet.exe", "detect", "cfg/yolov3.cfg", "yolov3.weights", image_path],
                        shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    out = [line for line in out.decode().split('\r\n')[1:-1] if line != '']
    # PoC improvements: Index objects and its respective confidence scores for faster querying
    list(map(print, out))

    os.chdir(cwd)

    # Step 2: Image Captioning
    description = captionize(image_path)
    # PoC improvements: Store the caption for detailed retrieval
    print('Caption:', description)
    print()
    
    # Step 3: Generate Triplets
    os.chdir('./ollie-openie')
    p = subprocess.Popen(['java', '-Xmx512m', '-jar', 'ollie-app-latest.jar'],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.stdin.write(description.encode())
    out, err = p.communicate()
    os.chdir(cwd)

    out = [line for line in out.decode().split('\r\n')[1:-1] if line != '']
    # PoC improvements: Index the triplets for keyword querying
    list(map(print, out))
    
    show_output('../yolo/predictions.jpg', 'Caption: ' + description, '\n'.join(out))