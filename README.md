# airtable-googlecalendar-sync
Periodic serverless script to sync airtable and google calendar

Specific use case that creates Google Calendar events for when I mark update specific fields for a record in Airtable

## Todo: 
* Configure GitHub Action to autodeploy 
Currently uses `aws lambda update-function-code --function-name airtable-script --zip-file fileb://function.zip`

To deploy to AWS, need to include in zip: `~/.local/share/virtualenvs/airtable-scripts-oewuQlhV/lib/python3.6/site-packages`

cd ~/.local/share/virtualenvs/airtable-scripts-oewuQlhV/lib/python3.6/site-packages
zip -r9 /mnt/c/Users/alexh/Desktop/hack/airtable-scripts/function.zip .
zip -g function.zip lambda_function.py request.py timeframe_sync.py service-account-credentials.json cal.py calendar_sync.py