import httplib2
import os.path, io
import pickle,mimetypes

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import discovery
from apiclient.http import MediaIoBaseDownload, MediaFileUpload

path = r'D:\Scripts\Python\Google-Drive-API-project\Google_Drive_API_scripts'

SCOPES = ['https://www.googleapis.com/auth/drive']
creds = None

if os.path.exists(path+'\\token.pickle'):
    with open(path+'\\token.pickle', 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            path+'\\client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open(path+'\\token.pickle', 'wb') as token:
        pickle.dump(creds, token)

drive_service = build('drive', 'v3', credentials=creds)

class Google_Drive_API:
    def __init__(self):
        self.drive_service = drive_service

    def download(id,path=os.path.join(os.getcwd(), 'temp.tmp')):
        request = drive_service.files().get_media(fileId=id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        with io.open(path,'wb') as f:
            fh.seek(0)
            f.write(fh.read())
    
    def listFiles(size=5,query=''):
        if len(query) > 0:
            query = "'" + query+"' in parents"
            results = drive_service.files().list(pageSize=size,fields='files(id, name)',q=query).execute()
        else:
            results = drive_service.files().list(
            pageSize=size,fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            for item in items:
                print(item['name'],'>',item['id'])
    
    def upload(files, mimetype='', folder_id=''):
        if (type(files) == list):
            pass
        else:
            files = [files]
        for file in files:
            try:
                if len(folder_id) > 0:
                    folder_id = folder_id
                    file_metadata = {
                        'name': file,
                        'parents': [folder_id]
                    }
                else:
                    file_metadata = {'name': file}
                if (len(mimetype) <= 0):
                    ext = os.path.splitext(file)[1]
                    mimetypes.init()
                    mimetypes.types_map[ext]
                    media = MediaFileUpload(file,
                                        mimetype=mimetype,
                                        resumable=True)
                file = drive_service.files().create(body=file_metadata,
                                                    media_body=media,
                                                    fields='id').execute()
                print('File ID: %s' % file.get('id'))
            except Exception as err:
                Type = type(err)
                Type = str(Type).replace('<class ','').replace('>',':')
                print(Type,err)

    def createFolder(folder_name,folder_id=''):
        if type(folder_name) == list:
            pass
        else:
            folder_name = [folder_name]
        for name in folder_name:
            try:
                if len(folder_id) > 0:
                    file_metadata = {
                        'name': name,
                        'parents': [folder_id],
                        'mimeType': 'application/vnd.google-apps.folder'
                    }
                else:
                    file_metadata = {
                        'name': folder_name,
                        'mimeType': 'application/vnd.google-apps.folder'
                    }
                file = drive_service.files().create(body=file_metadata,
                                                    fields='id').execute()
                print ('Folder ID: %s' % file.get('id'))
            except Exception as err:
                Type = type(err)
                Type = str(Type).replace('<class ','').replace('>',':')
                print(Type,err)

    def searchFile(size,query):
        query = 'name contains '+"'"+query+"'"
        results = drive_service.files().list(
        pageSize=size,fields="nextPageToken, files(id, name, kind, mimeType)",q=query).execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            for item in items:
                print('{0} ({1})'.format(item['name'], item['id']))