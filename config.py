import os
from os.path import join, dirname
from dotenv import load_dotenv


# load .env values
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# set up variables
AMP_PREFIX = 'www.google.com/amp/s/'
MERCURY_API_URL = os.getenv('MERCURY_API_URL')
MERCURY_API_KEY = os.getenv('MERCURY_API_KEY')
DO_NOT_REDIRECT = ['youtube.com', 'youtu.be', 'github.com', '.pdf', 'amazon.c', 'google.', 'goo.gl']
FALLBACK_REDIRECT_URL = 'https://googleweblight.com/?lite_url='
