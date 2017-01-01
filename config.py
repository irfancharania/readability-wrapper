import os
from os.path import join, dirname
from dotenv import load_dotenv


# load .env values
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# set up variables
MERCURY_API_KEY = os.getenv('MERCURY_API_KEY')
LINKS = 'redirect'
THEME = ''
DO_NOT_REDIRECT = ['youtube', 'dailymotion']