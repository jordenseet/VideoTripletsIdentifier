"""Main application package."""
from flask import Flask
app = Flask(__name__)
import routes.test
import routes.azure_comp_vision