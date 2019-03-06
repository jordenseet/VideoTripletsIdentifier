import os

from flask import Blueprint
from flask import current_app as app
from flask import redirect, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from .process import chunking, yolo

mod = Blueprint('files', __name__)


@mod.route('/upload', methods=['POST'])
def upload_file():
    directory_name = None
    print(request.files)
    if 'file' in request.files:  # videos and images both appear as 'file'
        file = request.files['file']  # gets the file
        if file.filename != '':
            extension = file.filename.split(".")[-1]  # gets the extension of the file
            if extension in app.config['ALLOWED_IMAGE_EXTENSIONS']:  # checks if the extension is an image allowed extension
                directory_name = app.config['IMAGE_UPLOAD_FOLDER']
            elif extension in app.config['ALLOWED_VIDEO_EXTENSIONS']:  # checks if the extension is a video allowed extension
                directory_name = app.config['VIDEO_UPLOAD_FOLDER']

            if directory_name:
                filename = secure_filename(file.filename)
                file.save(os.path.join(directory_name, filename))

                result = chunking(filename)
                if result == 'Success':
                    keyframes = [(video, app.config['KEYFRAME_UPLOAD_FOLDER'].split('/')[-1])
                                 for video in os.listdir(app.config['KEYFRAME_UPLOAD_FOLDER'])]
                    keyframes = sorted(keyframes, key=lambda x: int(''.join([ch for ch in x[0].split('.')[0] if ch.isdigit()])))
                    for video, folder in keyframes:
                        yolo(video)
    return redirect(url_for('index'))


@mod.route('/<filetype>/<filename>')
def uploaded_file(filetype, filename):
    filetype = filetype.lower()
    folder = app.config["IMAGE_UPLOAD_FOLDER"] if filetype == "images" \
        else app.config["VIDEO_UPLOAD_FOLDER"] if filetype == "videos" \
        else app.config["KEYFRAME_UPLOAD_FOLDER"] if filetype == "keyframes" \
        else app.config["ASSET_FOLDER"]
    return send_from_directory(os.path.join(app.config["BASE_FOLDER"], folder),
                               filename)


@mod.route('/<filetype>/<filename>/delete')
def delete_file(filetype, filename):
    filetype = filetype.lower()
    folder = app.config["IMAGE_UPLOAD_FOLDER"] if filetype == "images" \
        else app.config["VIDEO_UPLOAD_FOLDER"] if filetype == "videos" \
        else app.config["KEYFRAME_UPLOAD_FOLDER"] if filetype == "keyframes" \
        else app.config["ASSET_FOLDER"]
    filepath = os.path.join(folder, filename)
    if os.path.isfile(filepath):
        os.remove(filepath)

    return redirect(url_for('index'))
