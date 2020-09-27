import os
import requests
from funcy import get_in, partial
from datetime import datetime, timedelta
from dotenv import load_dotenv

from cal import calendar

# load env variables
load_dotenv()
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_NAME = os.getenv('BASE_NAME')
TABLE_NAME = os.getenv('TABLE_NAME')
CALENDAR_ID = os.getenv('CALENDAR_ID')  # Airtable Tasks

MAX_AIRTABLE_PATCH = 10

headers = {'Authorization': "Bearer " + AIRTABLE_API_KEY}
url = 'https://api.airtable.com/v0/{0}/{1}'.format(BASE_NAME, TABLE_NAME)
airtable_request = partial(requests.request, url=url, headers=headers)


def round_up_15_mins(tm):
    tm += timedelta(minutes = 14)

    return tm - timedelta(minutes=tm.minute % 15,
                             seconds=tm.second,
                             microseconds=tm.microsecond)


def get_updated_records():
    """ 
    Queries Airtable for records that have been updated, but not processed
    """
    # setting params
    fields = ["Name", "Deadline", "Status", "setTodayDate"]
    maxRecords = 100
    formula = "AND({Timeframe}='Today', NOT({Status}='Done'), {setTodayDate}='')"
    params = {"maxRecords": maxRecords,
              "fields[]": fields, 
              "filterByFormula": formula}

    # TODO: Error Handling
    return airtable_request('get', params=params).json()


def update_calendar_and_airtable(cal, response_json):
    payload = {"records": [], "typecast": True} # empty payload
    currentTime = round_up_15_mins(datetime.utcnow())

    for record in response_json['records']:
        name = get_in(record, ["fields", "Name"])
        print(name)
        cal.create_event(name, currentTime)

        if len(payload['records']) >= MAX_AIRTABLE_PATCH:
            r = airtable_request('patch', json=payload)
            payload = {"records": [], "typecast": True}

        payload['records'].append({
            "id": record['id'],
            "fields": {
                "setTodayDate": currentTime.isoformat()
            }})

    if len(payload['records']) > 0:
        r = airtable_request('patch', json=payload)


if __name__ == "__main__":
    response_json = get_updated_records()
    cal = calendar(CALENDAR_ID)
    update_calendar_and_airtable(cal, response_json)
