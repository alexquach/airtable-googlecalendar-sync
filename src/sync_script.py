""" sync_script.py

This module provides a script to synchronize a Airtable table and a Google Calendar.
"""
import os
from datetime import datetime, timedelta
from funcy import get_in, partial
from typing import Dict

from calendar_request import Calendar
from airtable_request import airtable_request, update_payload_state, send_nonempty_payload

CALENDAR_ID = os.getenv('CALENDAR_ID')  # Airtable Tasks
DAY_OF_WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
GCAL_COLOR_MAPPING = {
    "Done": "5",
    "Abandoned": "11"
} # some GCAL magic variables here


def round_up_15_mins(start: datetime) -> datetime:
    """ Helper method that rounds up to the nearest 15-min interval

    Args:
        start: The starting time
    
    Returns:
        The datetime rounded up to the nearest 15-min interval
    """
    start += timedelta(minutes=14)
    return start - timedelta(minutes=tm.minute % 15,
                          seconds=tm.second,
                          microseconds=tm.microsecond)


def get_active_records() -> Dict:
    """ Queries Airtable API for active records

    Retrieves the following fields:
        - Name: Main string identifier for the record
        - Deadline: String in the format (MM/DD/YYYY)
        - Status: Kanban-esque status ("Todo"/"In Progress"/"Done"/etc)
        - Deadline Group: Grouping of deadlines (Grouped by weeks + Today/Backlog)
        - calendarEventId: Corresponding Gcal calendar event id for the record
        - duration: estimated duration of event/task (in hours)
        - lastDeadline: the previous state of the `Deadline` field, used for sync'ing purposes
        - lastCalendarDeadline: the previous state of the `Deadline` field from the Calendar webhook,
            also used for sync'ing purposes to know when webhook last editted record

    The formula queries for Active Records, which are defined as:
        - Deadline set (i.e. 11/27/2020)
        - lastStatus not 'Done'

    Returns:
        Dict with the response from Airtable for the get request
    """
    fields = ["Name", "Deadline", "Status", "Deadline Group", "calendarEventId", "duration", 
        "lastDeadline", "lastCalendarDeadline", "lastName"]
    maxRecords = 100
    formula = "AND(NOT({Deadline}=''), NOT({lastStatus}='Done'))"
    params = {"maxRecords": maxRecords,
              "fields[]": fields,
              "filterByFormula": formula}

    # TODO: Error Handling
    return airtable_request('get', params=params).json()


def process_new_record(update_fields: dict, record: dict, calendar: Calendar) -> Dict:
    """ Detects and adds New Records to the update_field payload

    New Records are defined as:
        - lastDeadline is not set
        - Deadline is set

    Note:
        Events/Tasks created by the Gcal Webhook are considered New Records

    Does the following for New Records:
        1. Creates the initial Gcal Event, if not already created
        2. Populates the Deadline Group field in Airtable with the week-grouping or "Today"
        3. Populates the Day field in AirTable with the correct string "Mon"..."Sun"

    Args:
        update_fields: The payload dictionary that will be sent in a patch/post request to the Airtable API
        record: The individual record being processed
        calendar: The :obj:`calendar_request.Calendar` instance corresponding to the calendar out of which we're working

    Returns:
        An updated-version of `update_fields` to be sent to airtable in a patch/post request
    """
    deadline = get_in(record, ["fields", "Deadline"])
    lastDeadline = get_in(record, ["fields", "lastDeadline"])

    if deadline and not lastDeadline:
        name = get_in(record, ["fields", "Name"])
        airtable_record_id = get_in(record, ['id'])
        calendar_event_id = get_in(record, ["fields", "calendarEventId"])
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d") + timedelta(hours=16)

        if not calendar_event_id:
            created_event = calendar.create_event(name, deadline_date, airtable_record_id)

            update_fields.update({
                "calendarEventId": created_event['id'],
                "duration": 1,
                "lastDeadline": deadline,
            })
    return update_fields


def process_deadline_change(update_fields: dict, record: dict, calendar: Calendar) -> Dict:
    """ Detects records where the `Deadline` changed and updates the update_field payload accordingly

    A deadline change is detected when the `deadline` does not equal the `lastDeadline` field.

    Actions:
        1. Updates the Gcal event, if the detected deadline change did not originate from the webhook
        2. Update the `Deadline Group`, `Day`, and `lastDeadline` fields in Airtable

    Args:
        update_fields: The payload dictionary that will be sent in a patch/post request to the Airtable API
        record: The individual record being processed
        calendar: The :obj:`calendar_request.Calendar` instance corresponding to the calendar out of which we're working

    Returns:
        An updated-version of `update_fields` to be sent to airtable in a patch/post request
    """
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
            calendar.patch_event(calendar_event_id, airtable_record_id, start=deadline_date, duration=duration)
        
        update_fields.update({
            "Deadline Group": next_sunday, 
            "Day": DAY_OF_WEEK[deadline_date.weekday()],
            "lastDeadline": deadline
        })
    return update_fields


def process_name_change(update_fields: dict, record: dict, calendar: Calendar) -> Dict:
    """ Detects records where the `Name` changed and updates the update_field payload accordingly

    A deadline change is detected when the `Name` does not equal the `lastName` field.

    Actions:
        1. Updates the Gcal event
        2. Update the `lastName` field in Airtable

    Args:
        update_fields: The payload dictionary that will be sent in a patch/post request to the Airtable API
        record: The individual record being processed
        calendar: The :obj:`calendar_request.Calendar` instance corresponding to the calendar out of which we're working

    Returns:
        An updated-version of `update_fields` to be sent to airtable in a patch/post request
    """
    name = get_in(record, ["fields", "Name"])
    last_name = get_in(record, ["fields", "lastName"], "")

    if name != last_name:
        airtable_record_id = get_in(record, ['id'])
        calendar_event_id = get_in(record, ["fields", "calendarEventId"])

        # valid calendar_event_id
        if calendar_event_id:
            calendar.patch_event(calendar_event_id, airtable_record_id, title=name)
        
        print(f'new_name: {name}')
        update_fields.update({
            "lastName": name, 
        })
    return update_fields


def transition_today_record(update_fields: dict, record: dict) -> Dict:
    """ Transitions records with a deadline that corresponds to the current date
    
    Basically detects whether the `deadline` matches Today's actual date, and updates the
    `Deadline Group` to be "Today".

    Args:
        update_fields: The payload dictionary that will be sent in a patch/post request to the Airtable API
        record: The individual record being processed

    Returns:
        An updated-version of `update_fields` to be sent to airtable in a patch/post request
    """
    deadline = get_in(record, ["fields", "Deadline"])
    deadline_date = datetime.strptime(deadline, "%Y-%m-%d") + timedelta(hours=16)
    deadline_group = get_in(record, ["fields", "Deadline Group"], "")
    adjusted_datetime = datetime.today() - timedelta(hours=7)
    
    if adjusted_datetime.date() == deadline_date.date() and deadline_group != 'Today':
        update_fields.update({
            "Deadline Group": "Today",
        })
    return update_fields


def transition_done_record(update_fields: dict, record: dict, calendar: Calendar) -> Dict:
    """ Transitions recently marked "Done" and "Abandoned" `Status` records
    
    Does the following for "Done" and "Abandoned" Records
        1. Changes Google Calendar Event color to the completed color
        2. Sets the `lastStatus` field, which makes it an inactive record

    Args:
        update_fields: The payload dictionary that will be sent in a patch/post request to the Airtable API
        record: The individual record being processed
        calendar: The :obj:`calendar_request.Calendar` instance corresponding to the calendar out of which we're working

    Returns:
        An updated-version of `update_fields` to be sent to airtable in a patch/post request
    """
    status = get_in(record, ["fields", "Status"], "")

    if status == "Done" or status == "Abandoned":
        color_id = GCAL_COLOR_MAPPING[status]
        calendar_event_id = get_in(record, ["fields", "calendarEventId"])
        airtable_record_id = get_in(record, ["id"])

        if calendar_event_id:
            calendar.patch_event(calendar_event_id, airtable_record_id, color_id=color_id)

        update_fields.update({
            "lastStatus": "Done",
        })
    return update_fields


def update_records(calendar: Calendar, active_records: dict):
    """ Patches Airtable with updates to `Deadline Group` field based off of deadline

    Iterates through each active record, and applies the :func:`process_new_record`,
    :func:`process_deadline_change`, :func:`transition_today_record`, and 
    :func:`transition_done_record` logic methods. 

    As the method iterates through the records, the :func:`update_payload_state` method
    handles the request paging to appease the Airtable API's limits. The leftover payload is
    sent to the Airtable API with :func:`send_nonempty_payload`

    Args: 
        calendar: The :obj:`calendar_request.Calendar` instance corresponding to the calendar out of which we're working
        active_records: All of the active records in the Airtable table
    """
    payload = {"records": [], "typecast": True}  

    for record in active_records['records']:
        # paginate payload, if necessary
        payload = update_payload_state(payload, 'patch')
        
        update_fields = dict()
        update_fields = process_new_record(update_fields, record, calendar)
        update_fields = process_deadline_change(update_fields, record, calendar)
        update_fields = process_name_change(update_fields, record, calendar)
        update_fields = transition_today_record(update_fields, record)
        update_fields = transition_done_record(update_fields, record, calendar)

        if update_fields:
            payload['records'].append({
                "id": record['id'],
                "fields": update_fields
            })

    # patch request to Airtable
    send_nonempty_payload(payload, 'patch')


def sync():
    """ Retrieves active records and then updates the records with outlined logic """
    active_records = get_active_records()
    calendar = Calendar(CALENDAR_ID)
    update_records(calendar, active_records)


if __name__ == "__main__":
    sync()
