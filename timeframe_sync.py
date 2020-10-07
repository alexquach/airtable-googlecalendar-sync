import os
from datetime import datetime, timedelta
from funcy import get_in, partial

from request import airtable_request, MAX_AIRTABLE_PATCH

TIMEFRAME_TO_DAY_DIFFERENTIAL = {
    "Today": 0,
    "Soon": 5,
    'Weekish': 10
}


def get_records_with_deadlines():
    """ 
    Queries Airtable for records that have a valid deadline
    """
    # setting params
    fields = ["Name", "Deadline", "Status", "setTodayDate"]
    maxRecords = 100
    formula = "AND(NOT({Deadline}=''), NOT({Status}='Done'))"
    params = {"maxRecords": maxRecords,
              "fields[]": fields,
              "filterByFormula": formula}

    # TODO: Error Handling
    return airtable_request('get', params=params).json()


def patch_updated_deadline(response_json):
    payload = {"records": [], "typecast": True}  # empty payload

    for record in response_json['records']:
        deadline = get_in(record, ["fields", "Deadline"])
        date = datetime.strptime(deadline, "%Y-%m-%d")
        day_delta = (date - datetime.today()).days

        if len(payload['records']) >= MAX_AIRTABLE_PATCH:
            r = airtable_request('patch', json=payload)
            payload = {"records": [], "typecast": True}

        for timeframe in TIMEFRAME_TO_DAY_DIFFERENTIAL:
            if day_delta < TIMEFRAME_TO_DAY_DIFFERENTIAL[timeframe]:

                payload['records'].append({
                    "id": record['id'],
                    "fields": {
                        "Timeframe": timeframe
                    }})
                break

    if len(payload['records']) > 0:
        r = airtable_request('patch', json=payload)


def timeframe_sync():
    response_json = get_records_with_deadlines()
    patch_updated_deadline(response_json)


if __name__ == "__main__":
    timeframe_sync()
