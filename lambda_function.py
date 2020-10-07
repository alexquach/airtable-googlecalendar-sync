from timeframe_sync import timeframe_sync
from calendar_sync import calendar_sync

def lambda_handler(event, context):
    timeframe_sync()
    calendar_sync()
    return