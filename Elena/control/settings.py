# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

MAPBOX_KEY = os.getenv('MAPBOX_KEY')
