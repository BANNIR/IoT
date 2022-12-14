import base64
from email.message import EmailMessage

import os.path
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
serv_email = 'elemtestbed@gmail.com'

# mail setup
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            './client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('gmail', 'v1', credentials=creds)


def send_mail(subject, body, to = 'elemtestbed@gmail.com'):
    service = build('gmail', 'v1', credentials=creds)
    try:
        message = EmailMessage()

        message.set_content(body)

        message['To'] = to
        message['From'] = serv_email
        message['Subject'] = subject

        raw_string = base64.urlsafe_b64encode(message.as_bytes()).decode()

        fMessage = (service.users().messages().send(userId='me', body={'raw': raw_string}).execute())
    except HttpError as error:
        print('An error occurred: %s' % error)
        fMessage = None
    return fMessage

    
def get_mails(maxResults = 100):
    service = build('gmail', 'v1', credentials=creds)
    try:
        messages = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=maxResults).execute()
    except HttpError as error:
        print('An error occurred: %s' % error)
        messages = None
    return messages

def get_mail_ids(maxResults = 100):
    messages = get_mails(maxResults)
    if messages is not None:
        mailIds = [message['id'] for message in messages['messages']]
    else:
        mailIds = None
    return mailIds

def get_mail(mailId):
    service = build('gmail', 'v1', credentials=creds)
    try:
        message = service.users().messages().get(userId='me', id=mailId).execute()
    except HttpError as error:
        print('An error occurred: %s' % error)
        message = None
    return message

def read_mail_body(mailId):
    message = get_mail(mailId)
    if message is not None:
        body = message['snippet']
    else:
        body = None
    return body

def read_mail_subject(mailId):
    message = get_mail(mailId)
    if message is not None:
        subject = message['payload']['headers'][0]['value']
    else:
        subject = None
    return subject

def read_mail_timestamp(mailId):
    message = get_mail(mailId)
    if message is not None:
        timestamp = message['internalDate']
    else:
        timestamp = None
    return timestamp

# if __name__ == '__main__':
#     print('Should testbed send or read emails?')
#     print('1. Send')
#     print('2. Read')
#     choice = input('Enter your choice: ')
#     if choice == '1':
#         print('Sending email to the testbed')
#         subject = input('Enter subject: ')
#         body = input('Enter body: ')
#         send_mail(subject, body)
#     elif choice == '2':
#         print('Reading latest email from the testbed')
#         email_id = get_mail_ids(1)
#         reply = read_mail_body(email_id[0])
#         date = read_mail_timestamp(email_id[0])
#         reply = reply.lower()
#         print("Info of latest email:")
#         print(reply)
#         print(date)