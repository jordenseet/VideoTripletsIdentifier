import os
from flask import Flask
from flask_bootstrap import Bootstrap


def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    app.config.from_pyfile('../config.py')

    from app.model import db
    db.init_app(app)

    from app.views import files, process
    app.register_blueprint(files.mod, url_prefix='/files')
    app.register_blueprint(process.mod, url_prefix='/process')

    folders = (
        app.config['IMAGE_UPLOAD_FOLDER'],
        app.config['VIDEO_UPLOAD_FOLDER'],
        app.config['KEYFRAME_UPLOAD_FOLDER']
    )

    # Ensure that the necessary folders exist
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    return app
