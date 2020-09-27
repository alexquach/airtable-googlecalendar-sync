# airtable-googlecalendar-sync
Periodic serverless script to sync airtable and google calendar

Specific use case that creates Google Calendar events for when I mark update specific fields for a record in Airtable

## Todo: 
* Configure GitHub Action to autodeploy 
Currently uses `aws lambda update-function-code --function-name airtable-script --zip-file fileb://function.zip`