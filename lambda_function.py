from timeframe_sync import timeframe_sync

def lambda_handler(event, context):
    timeframe_sync()
    return