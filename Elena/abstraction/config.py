import os
from dotenv import load_dotenv

load_dotenv()

API={}
API['googleapikey']=os.getenv('GOOGLEAPIKEY')