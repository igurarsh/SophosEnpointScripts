from __future__ import print_function
from webbrowser import get
import requests
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Stuff for Google Sheets API
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly',
        'https://www.googleapis.com/auth/spreadsheets']

# Google Sheets API Reference
SAMPLE_SPREADSHEET_ID = ''
SAMPLE_RANGE_NAME = 'A1'

# Data to be enetered in Sheets 
new_values =[
    # cell values
    ['Hostname','Platform','Temper Password']
]

# Functions for Sophos API
def execute():

    # Parameters for the API
    requestUrl = "https://api-us03.central.sophos.com/endpoint/v1/endpoints"
    requestHeaders = {
        "Authorization": "Bearer ",
        "X-Tenant-ID": "",
        "Accept": "application/json"
    }
    query_pram = {
        'pageSize': '500'
    }

    # Making the API request
    request = requests.get(requestUrl, headers=requestHeaders, params=query_pram)

    jsonResoponse = request.json()
    temp_data = jsonResoponse['items']

    # Praising the JSON data
    #for data in jsonResoponse.items():
     #   print("ID: "+data['items'][0]['id']+" Name: "+data['items'][0]['associatedPerson']['name'])    
        
    #print (jsonResoponse)
    temp_name = ""
    temp_passwd = ""
    temp_platform = ""

    for data in temp_data:
        temp_name = data['hostname']
        temp_passwd = getTemperPassword(data['id'])
        temp_platform = data['os']['platform']

        # Appending values to main DICT
        new_values.append([temp_name,temp_platform,temp_passwd])
        #print(temp_name+"   "+temp_passwd+"  "+data['os']['platform'])
        #print("ID: "+data['id']+" Name: "+data['hostname']+" Temper Password: "+getTemperPassword(data['id']))

    sheetAPI(new_values)

# API for Getting Temper Passwords from Sophos
def getTemperPassword(id):
    requestUrl = "https://api-us03.central.sophos.com/endpoint/v1/endpoints/"+id+"/tamper-protection"
    requestHeaders = {
        "Authorization": "Bearer ",
        "X-Tenant-ID": "",
        "Accept": "application/json"
    }

    request = requests.get(requestUrl, headers=requestHeaders)

    jsonResoponse = request.json()

    #for key, data in jsonResoponse.items():
        #print(key, ":" ,data)

    return jsonResoponse["password"]

# Function for Sheets API
def sheetAPI(data):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Calling the sevice for Google Sheets API
    sheets_service = build('sheets', 'v4', credentials=creds)

    # Sending the data to selected sheet
    body={
        'values': data
    }

    try:
        new_result = sheets_service.spreadsheets().values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME,valueInputOption='RAW', body=body).execute()
        print('Login_Audit Google Sheet Exported Successfully\n')
    except:
            print("Error Occured")

if __name__ == "__main__":
  execute()
