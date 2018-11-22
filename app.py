from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os.path
import requests, os

app = Flask(__name__)
app.config.from_pyfile('config.py')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        print(request.files)
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # return redirect(url_for('uploaded_file', filename=filename))
    
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', uploaded_files=uploaded_files)


@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/images/<filename>/delete')
def delete_file(filename):
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.isfile(image_path):
        os.remove(image_path)

    return redirect(url_for('index'))


@app.route('/azure', methods=['GET'])
def get_captions():
    # Set image_path to the local path of an image that you want to analyze.
    filename = request.args['file'] if 'file' in request.args else ''
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

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