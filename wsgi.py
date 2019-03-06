import os
import os.path

from app import create_app
from flask import render_template

app = create_app()


@app.route('/')
def index():
    # adds all file names and the file types to a tuple array
    uploaded_files = [
        *[(video, app.config['VIDEO_UPLOAD_FOLDER'].split('/')[-1])
          for video in os.listdir(app.config['VIDEO_UPLOAD_FOLDER'])],
        *[(video, app.config['IMAGE_UPLOAD_FOLDER'].split('/')[-1])
          for video in os.listdir(app.config['IMAGE_UPLOAD_FOLDER'])]
    ]
    keyframes = [(video, app.config['KEYFRAME_UPLOAD_FOLDER'].split('/')[-1])
                 for video in os.listdir(app.config['KEYFRAME_UPLOAD_FOLDER'])]
    keyframes = sorted(keyframes, key=lambda x: int(''.join([ch for ch in x[0].split('.')[0] if ch.isdigit()])))

    print(uploaded_files)
    uploaded_files = tuple(uploaded_files)  # casts the list to tuple
    return render_template(
        'index.html',
        uploaded_files=uploaded_files,
        keyframes=keyframes)


# @app.route('/upload_video_to_azure', methods=['GET'])
# def upload_video_to_azure():
#     # Set video_path to the local path of a video that you want to analyze.
#     filename = request.args['file'] if 'file' in request.args else ''
#     token = get_account_access_token()
#     params = {'accessToken': token, 'name': filename}
#     headers = {'Content-Type': 'multipart/form-data'}
#     video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], filename)
#     files = {'file': open(video_path, 'rb').read()}
#     response = requests.post(app.config['VIDEO_INDEXER_VIDEO_UPLOAD_URL'],
#                              params=params, headers=headers, files=files)
#     response.raise_for_status()
#     result = response.json()
#     return result


# def get_account_access_token():
#     subscription_key = app.config['VIDEO_INDEXER_SUBSCRIPTION_KEY']
#     location         = app.config['VIDEO_INDEXER_LOCATION']
#     accountId        = app.config['VIDEO_INDEXER_ACCOUNT_ID']

#     headers    = {'Ocp-Apim-Subscription-Key': subscription_key}
#     params     = {'allowEdit': 'true'}
#     response   = requests.get(app.config['VIDEO_INDEXER_ACCOUNT_AUTH_URL'], headers=headers, params=params)
#     response.raise_for_status()
#     token = response.json()
#     return token


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
