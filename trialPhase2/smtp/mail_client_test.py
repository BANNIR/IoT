import yagmail
from yagmail.oauth2 import refresh_authorization

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.modify']
access_token = ''
expires_in = 0
refresh_token = ''
user_email = 'elemtestbed@gmail.com'

# mail setup
yag = yagmail.SMTP(user_email, oauth2_file='oauth.json')
inf = {
    "google_client_id": yag.credentials['google_client_id'],
    "google_client_secret": yag.credentials['google_client_secret'],
    "google_refresh_token": yag.credentials['google_refresh_token']
}
access_token, expires_in = refresh_authorization(**inf)
refresh_token = yag.credentials['google_refresh_token']
oauth_token = yag.get_oauth_string(yag.user, inf)

def send_mail(subject, body, to = 'elemtestbed@gmail.com'):
    yag.send(to=to, subject=subject, contents=body)
    
def get_mails():

    token = {
        "access_token": access_token,
        "expires_in": expires_in,
        "refresh_token": refresh_token,
        "scope": "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify",
        "client_id": yag.credentials['google_client_id'],
        "client_secret": yag.credentials['google_client_secret'],
        "token_type": "Bearer"
    }

    creds = Credentials.from_authorized_user_info(token)
    service = build('gmail', 'v1', credentials=creds)

    messages = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    for message in messages['messages']:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        msg_headers = msg['payload']['headers']
        msg_from = filter(lambda hdr: hdr['name'] == 'From', msg_headers)
        msg_from = list(msg_from)[0]
        # print('From: ' + msg_from['value'])
        # print('> ' + msg['snippet'])
        # print('-----------------------')

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
#         print('Reading emails from the testbed')
#         get_mails()