# airtable-googlecalendar-sync
Periodic serverless script to sync airtable and google calendar

Specific use case that creates Google Calendar events for when I mark update specific fields for a record in Airtable

## Todo: 
* Configure GitHub Action to autodeploy 

To deploy to AWS, need to include in zip: ~/.local/share/virtualenvs/airtable-scripts-oewuQlhV/lib/python3.6/site-packages

cd ~/.local/share/virtualenvs/airtable-scripts-oewuQlhV/lib/python3.6/site-packages zip -r9 /mnt/c/Users/alexh/Desktop/hack/airtable-scripts/function.zip . zip -g -j function.zip src/* service-account-credentials.json

To update AWS Lambda, currently uses aws lambda update-function-code --function-name airtable-script --zip-file fileb://function.zip