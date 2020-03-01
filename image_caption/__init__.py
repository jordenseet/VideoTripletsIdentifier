import os
import numpy as np

from flask import current_app as app
from pickle import load
from numpy import argmax
from keras.preprocessing.sequence import pad_sequences
from keras.applications.vgg16 import VGG16
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.models import Model
from keras.models import load_model
from image_caption.utility import *

dir_path = os.path.dirname(os.path.realpath(__file__))

try:
    tokenizer
    max_length
    model
    vgg_model
except:
    # load the tokenizer
    tokenizer = load(open(os.path.join(dir_path, 'tokenizer.pkl'), 'rb'))
    # pre-define the max sequence length (from training)
    max_length = 34
    # load the model
    model = load_model(os.path.join(dir_path, 'model_19.h5'))

    vgg_model = VGG16()
    vgg_model.layers.pop()
    vgg_model = Model(inputs=vgg_model.inputs, outputs=vgg_model.layers[-1].output)


def predict_on_batch(X_test):
    # custom batched prediction loop to avoid memory leak issues for now in the model.predict call
    y_pred_probs = np.empty([len(X_test), VOCAB_SIZE], dtype=np.float32)  # pre-allocate required memory for array for efficiency

    BATCH_INDICES = np.arange(start=0, stop=len(X_test), step=BATCH_SIZE)  # row indices of batches
    BATCH_INDICES = np.append(BATCH_INDICES, len(X_test))  # add final batch_end row

    for index in np.arange(len(BATCH_INDICES) - 1):
        batch_start = BATCH_INDICES[index]  # first row of the batch
        batch_end = BATCH_INDICES[index + 1]  # last row of the batch
        y_pred_probs[batch_start:batch_end] = vgg_model.predict_on_batch(X_test[batch_start:batch_end])

    return y_pred_probs


def captionize_batch():
    result = []
    keyframes = [video for video in os.listdir(app.config['KEYFRAME_UPLOAD_FOLDER'])]
    for video in keyframes:
        filename = f"{app.config['KEYFRAME_UPLOAD_FOLDER']}/{video}"
        image = load_img(filename, target_size=(224, 224))
        image = img_to_array(image)
        image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
        image = preprocess_input(image)
        result.append(image)

    result = predict_on_batch(result)
    print(result)
    return result


def extract_features(filename):
    image = load_img(filename, target_size=(224, 224))
    image = img_to_array(image)
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    image = preprocess_input(image)
    feature = vgg_model.predict(image, verbose=0)
    return feature


def captionize(photo):
    features = extract_features(photo)
    return generate_desc(model, tokenizer, features, max_length)[len('startseq '):-len(' endseq')]


if __name__ == "__main__":
    # load and prepare the photograph
    photo = extract_features('example.jpg')
    # generate description
    description = generate_desc(model, tokenizer, photo, max_length)
    print(description)