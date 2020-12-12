from sync_script import sync

def lambda_handler(event, context):
    sync()
    return