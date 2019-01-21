ASSET_FOLDER = "./assets"
IMAGE_UPLOAD_FOLDER = "./uploads/images"
VIDEO_UPLOAD_FOLDER = "./uploads/videos"
KEYFRAME_UPLOAD_FOLDER = "./uploads/keyframes"
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
ALLOWED_VIDEO_EXTENSIONS = set(['mp4'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

OCP_APIM_SUBSCRIPTION_KEY = "ac03e86a78db457db7e2b1e6f9859947"
AZURE_VISION_BASE_URL = "https://westcentralus.api.cognitive.microsoft.com/vision/v2.0"  # noqa
AZURE_VISION_ANALYZE_URL = f"{AZURE_VISION_BASE_URL}/analyze"

VIDEO_INDEXER_ACCOUNT_ID = "8a38d5b0-4348-4d01-b98b-3c8eca1d4c2c"
VIDEO_INDEXER_LOCATION = "trial"
VIDEO_INDEXER_SUBSCRIPTION_KEY = "64e5d9314d1144d3affae44c99fe61d1"
VIDEO_INDEXER_BASE_URL = "https://api.videoindexer.ai"
VIDEO_INDEXER_ACCOUNT_AUTH_URL = f"{VIDEO_INDEXER_BASE_URL}/auth/{VIDEO_INDEXER_LOCATION}/Accounts/{VIDEO_INDEXER_ACCOUNT_ID}/AccessToken"  # noqa
VIDEO_INDEXER_VIDEO_UPLOAD_URL = f"{VIDEO_INDEXER_BASE_URL}/{VIDEO_INDEXER_LOCATION}/Accounts/{VIDEO_INDEXER_ACCOUNT_ID}/Videos"  # noqa

SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
