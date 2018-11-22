IMAGE_UPLOAD_FOLDER = "./images"
VIDEO_UPLOAD_FOLDER = "./videos"
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
ALLOWED_VIDEO_EXTENSIONS = set(['mp4'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

OCP_APIM_SUBSCRIPTION_KEY = "ac03e86a78db457db7e2b1e6f9859947"
AZURE_VISION_BASE_URL = "https://westcentralus.api.cognitive.microsoft.com/vision/v2.0/"
AZURE_VISION_ANALYZE_URL = f"{AZURE_VISION_BASE_URL}/analyze"