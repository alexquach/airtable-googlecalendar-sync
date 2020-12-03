import os
from datetime import datetime, timedelta
from funcy import get_in, partial

from cal import calendar
from request import airtable_request, update_payload_state, send_nonempty_payload

CALENDAR_ID = os.getenv('CALENDAR_ID')  # Airtable Tasks
DAY_OF_WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
GCAL_COLOR_MAPPING = {
    "Done": "5",
    "Abandoned": "11"
} # some GCAL magic variables here


def round_up_15_mins(tm):
    tm += timedelta(minutes=14)

    return tm - timedelta(minutes=tm.minute % 15,
                          seconds=tm.second,
                          microseconds=tm.microsecond)


def get_active_records():
    """ Queries Airtable for records that have a valid deadline

    Active Records are defined as:
        Deadline set (i.e. 11/27/2020)
        lastStatus not 'Done'
    """
    fields = ["Name", "Deadline", "Status", "Deadline Group", "calendarEventId", "duration", "lastDeadline", "lastCalendarDeadline"]
    maxRecords = 100
    formula = "AND(NOT({Deadline}=''), NOT({lastStatus}='Done'))"
    params = {"maxRecords": maxRecords,
              "fields[]": fields,
              "filterByFormula": formula}

    # TODO: Error Handling
    return airtable_request('get', params=params).json()


def process_new_record(update_fields, record, cal):
    """ 
    Does the following for New Records:
        1. Creates the initial Gcal Event
        2. Populates the Deadline Group and Day columns in AirTable

    New Records are defined as:
        lastDeadline is not set
        Deadline is set
    """
    deadline = get_in(record, ["fields", "Deadline"])
    lastDeadline = get_in(record, ["fields", "lastDeadline"])

    if deadline and not lastDeadline:
        name = get_in(record, ["fields", "Name"])
        airtable_record_id = get_in(record, ['id'])
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d") + timedelta(hours=16)

        created_event = cal.create_event(name, deadline_date, airtable_record_id)

        update_fields.update({
            "calendarEventId": created_event['id'],
            "duration": 1,
            "lastDeadline": deadline,
        })
    return update_fields


def process_deadline_change(update_fields, record, cal):
    deadline = get_in(record, ["fields", "Deadline"])
    last_deadline = get_in(record, ["fields", "lastDeadline"], "")

    if deadline != last_deadline:
        calendar_event_id = get_in(record, ["fields", "calendarEventId"])
        duration = get_in(record, ["fields", "duration"])
        lastCalendarDeadline = get_in(record, ["fields", "lastCalendarDeadline"], "")[0:10]
        airtable_record_id = get_in(record, ["id"])
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d") + timedelta(hours=16)
        days_to_sunday = 6 - deadline_date.weekday()
        next_sunday = (deadline_date + timedelta(days=days_to_sunday)).strftime("%m/%d")

        if not duration:
            duration = 1

        # valid calendar_event_id; and wasn't recently updated by gcal webhook
        if calendar_event_id and lastCalendarDeadline != deadline:
            print(deadline)
            print(lastCalendarDeadline)
            cal.patch_event(calendar_event_id, airtable_record_id, start=deadline_date, duration=duration)
        
        update_fields.update({
            "Deadline Group": next_sunday, 
            "Day": DAY_OF_WEEK[deadline_date.weekday()],
            "lastDeadline": deadline
        })
    return update_fields


def transition_today_record(update_fields, record):
    """ Transitions records with a deadline that corresponds to the current date"""
    deadline = get_in(record, ["fields", "Deadline"])
    deadline_date = datetime.strptime(deadline, "%Y-%m-%d") + timedelta(hours=16)
    deadline_group = get_in(record, ["fields", "Deadline Group"], "")
    adjusted_datetime = datetime.today() - timedelta(hours=7)
    
    if adjusted_datetime.date() == deadline_date.date() and deadline_group != 'Today':

        update_fields.update({
            "Deadline Group": "Today",
        })
    return update_fields


def transition_done_record(update_fields, record, cal):
    """ Transitions `Done` and `Abandoned` Status records
    
    Does the following for Done Records
        1. Changes Google Calendar Event color
        2. Sets the `lastStatus` field, which makes it an inactive record
    """
    status = get_in(record, ["fields", "Status"], "")

    if status == "Done" or status == "Abandoned":
        color_id = GCAL_COLOR_MAPPING[status]
        calendar_event_id = get_in(record, ["fields", "calendarEventId"])
        airtable_record_id = get_in(record, ["id"])

        if calendar_event_id:
            cal.patch_event(calendar_event_id, airtable_record_id, color_id=color_id)

        update_fields.update({
            "lastStatus": "Done",
        })
    return update_fields


def update_records(cal, active_records):
    """ Patches Airtable with updates to `Deadline Group` field based off of deadline
    """
    payload = {"records": [], "typecast": True}  

    for record in active_records['records']:
        # paginate payload, if necessary
        payload = update_payload_state(payload, 'patch')
        
        update_fields = dict()
        update_fields = process_new_record(update_fields, record, cal)
        update_fields = process_deadline_change(update_fields, record, cal)
        update_fields = transition_today_record(update_fields, record)
        update_fields = transition_done_record(update_fields, record, cal)

        if update_fields:
            payload['records'].append({
                "id": record['id'],
                "fields": update_fields
            })

    # patch request to Airtable
    send_nonempty_payload(payload, 'patch')


def timeframe_sync():
    active_records = get_active_records()
    cal = calendar(CALENDAR_ID)
    update_records(cal, active_records)


if __name__ == "__main__":
    timeframe_sync()
