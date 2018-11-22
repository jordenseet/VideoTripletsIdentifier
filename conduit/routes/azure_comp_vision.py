import logging

from flask import request, jsonify;
from conduit import app;
import requests
from PIL import Image
from io import BytesIO
logger = logging.getLogger(__name__)

@app.route('/azure', methods=['GET'])
# @app.route('/square', methods=['POST'])
def get_captions():
    # data = request.get_json();
    # logging.info("data sent for evaluation {}".format(data))
    # inputValue = data.get("input");
    # result = inputValue * inputValue
    # logging.info("My result :{}".format(result))
    # return jsonify(result);

    # Replace <Subscription Key> with your valid subscription key.
    subscription_key = "ac03e86a78db457db7e2b1e6f9859947"
    assert subscription_key

    vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v2.0/"

    analyze_url = vision_base_url + "analyze"

    # Set image_path to the local path of an image that you want to analyze.
    image_path = "images/train.jpg"

    # Read the image into a byte array
    image_data = open(image_path, "rb").read()
    headers    = {'Ocp-Apim-Subscription-Key': subscription_key,
                  'Content-Type': 'application/octet-stream'}
    params     = {'visualFeatures': 'Categories,Description,Color'}
    response = requests.post(
        analyze_url, headers=headers, params=params, data=image_data)
    response.raise_for_status()

    # The 'analysis' object contains various fields that describe the image. The most
    # relevant caption for the image is obtained from the 'description' property.
    analysis = response.json()
    print(analysis)
    image_caption = analysis["description"]["captions"][0]["text"].capitalize()
    return image_caption
    