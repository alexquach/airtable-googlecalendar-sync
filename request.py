import os
import requests
from funcy import get_in, partial
from dotenv import load_dotenv

from cal import calendar

# load env variables
load_dotenv()
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_NAME = os.getenv('BASE_NAME')
TABLE_NAME = os.getenv('TABLE_NAME')

MAX_AIRTABLE_PATCH = 10

headers = {'Authorization': "Bearer " + AIRTABLE_API_KEY}
url = 'https://api.airtable.com/v0/{0}/{1}'.format(BASE_NAME, TABLE_NAME)

airtable_request = partial(requests.request, url=url, headers=headers)