import pickle
import mimetypes
import base64
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

path = r'D:\Scripts\Python\Gmail-API-project\Gmail_API_scripts'
SCOPES = ['https://mail.google.com/']

creds = None

if os.path.exists(path+'\\token.pickle'):
    with open(path+'\\token.pickle', 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            path+'\\credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open(path+'\\token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('gmail', 'v1', credentials=creds, cache_discovery=False)

class Gmail_API:
    def __init__(self):
        self.service = service
    def getLabel(userId='me',i=''):

        if len(i) > 0:
            results = service.users().labels().list(userId=userId,id=i).execute()
        else:
            results = service.users().labels().list(userId=userId).execute()
        labels = results.get('labels', [])
        if not labels:
            print('No labels found.')
        else:
            print('Labels:')
            for label in labels:
                print(label['name'])
    def getMailId(userId='me',labelIds=None,query=None,maxResults=None):

        messageIds = service.users().messages().list(userId=userId,labelIds=labelIds,q=query,maxResults=maxResults).execute()
        if messageIds['resultSizeEstimate'] == 0:
            return messageIds
        Ids = {}
        Ids['Ids'] = []
        for ids in messageIds['messages']:
            Ids['Ids'].append(ids['id'])
        return Ids
        
    def getMail(ids,userId='me'):

        message = service.users().messages().get(userId=userId,id=ids).execute()
        From = message['payload']['headers'][2]['value']
        To = message['payload']['headers'][3]['value']
        Subject = message['payload']['headers'][4]['value']
        Date = message['payload']['headers'][5]['value']
        Body = message['snippet']
        messageContent = {
                            'From': From,
                            'To': To,
                            'Subject': Subject,
                            'Date': Date,
                            'Body': Body
        }
        return messageContent
        
    def createMail(To, message_text, userId='me', From=None, Subject=None):

        if type(To) == list:
            for to in To:
                mimeContent = MIMEText(message_text)
                mimeContent['to'] = to
                mimeContent['from'] = From
                mimeContent['subject'] = Subject
                raw = base64.urlsafe_b64encode(mimeContent.as_bytes()).decode()
                body = {'raw': raw}

                service.users().messages().send(userId=userId, body=body).execute()
        else:
            mimeContent = MIMEText(message_text)
            mimeContent['to'] = To
            mimeContent['from'] = From
            mimeContent['subject'] = Subject
            raw = base64.urlsafe_b64encode(mimeContent.as_bytes()).decode()
            body = {'raw': raw}

            service.users().messages().send(userId=userId, body=body).execute()
    
    def deleteMail(ids, userId='me'):

        service.users().messages().delete(userId='me', id=ids).execute()