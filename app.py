from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import os.path
import requests
import os

from app import files, process

app = Flask(__name__)
Bootstrap(app)
app.config.from_pyfile('config.py')

app.register_blueprint(files.mod, url_prefix='/files')
app.register_blueprint(process.mod, url_prefix='/process')

for folder in (app.config['IMAGE_UPLOAD_FOLDER'], app.config['VIDEO_UPLOAD_FOLDER'], app.config['KEYFRAME_UPLOAD_FOLDER']):
    if not os.path.isdir(folder):
        print(f'Created {folder}')
        os.mkdir(folder)


# @app.route('/', methods=['GET', 'POST'])
@app.route('/')
def index():
    # directory_name = None
    # if request.method == "POST":
    #     print(request.files)
    #     if 'file' in request.files:  # videos and images both appear as 'file'
    #         file = request.files['file']  # gets the file
    #         if file.filename != '':
    #             extension = file.filename.split(".")[-1]  # gets the extension of the file
    #             if extension in app.config['ALLOWED_IMAGE_EXTENSIONS']:  # checks if the extension is an image allowed extension
    #                 directory_name = app.config['IMAGE_UPLOAD_FOLDER']
    #             elif extension in app.config['ALLOWED_VIDEO_EXTENSIONS']:  # checks if the extension is a video allowed extension
    #                 directory_name = app.config['VIDEO_UPLOAD_FOLDER']

    #             if directory_name:
    #                 filename = secure_filename(file.filename)
    #                 file.save(os.path.join(directory_name, filename))

    uploaded_files = []
    # adds all file names and the file types to a tuple array
    uploaded_files.extend((video, app.config['VIDEO_UPLOAD_FOLDER'][2:]) for video in os.listdir(app.config['VIDEO_UPLOAD_FOLDER']))
    uploaded_files.extend((video, app.config['IMAGE_UPLOAD_FOLDER'][2:]) for video in os.listdir(app.config['IMAGE_UPLOAD_FOLDER']))
    keyframes = [(video, app.config['KEYFRAME_UPLOAD_FOLDER'][2:]) for video in os.listdir(app.config['KEYFRAME_UPLOAD_FOLDER'])]

    # print(uploaded_files)
    uploaded_files = tuple(uploaded_files)  # casts the list to tuple
    return render_template('index.html', uploaded_files=uploaded_files, keyframes=keyframes)


@app.route('/upload_video_to_azure', methods=['GET'])
def upload_video_to_azure():
    # Set video_path to the local path of a video that you want to analyze.
    filename = request.args['file'] if 'file' in request.args else ''
    token = get_account_access_token()
    params = {'accessToken': token, 'name': filename}
    headers = {'Content-Type': 'multipart/form-data'}
    video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], filename)
    files = {'file': open(video_path, 'rb').read()}
    response = requests.post(app.config['VIDEO_INDEXER_VIDEO_UPLOAD_URL'],
                             params=params, headers=headers, files=files)
    response.raise_for_status()
    result = response.json()
    return result


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
