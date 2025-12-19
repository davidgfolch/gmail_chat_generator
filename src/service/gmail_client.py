
import os
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from .. import config

class GmailClient:
    def __init__(self):
        self.creds = self._get_credentials()
        self.service = build('gmail', 'v1', credentials=self.creds)

    def _get_credentials(self):
        """Gets valid user credentials from storage."""
        os.makedirs(config.CREDENTIALS_DIR, exist_ok=True)
        creds = None
        if os.path.exists(config.TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(config.CREDENTIALS_FILE):
                    raise FileNotFoundError(f"Credentials file not found at '{config.CREDENTIALS_FILE}'.")
                flow = InstalledAppFlow.from_client_secrets_file(config.CREDENTIALS_FILE, config.SCOPES)
                creds = flow.run_local_server(port=0)
            with open(config.TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        return creds

    def search_messages(self, query):
        """Searches for messages matching the query."""
        try:
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            while 'nextPageToken' in results:
                page_token = results['nextPageToken']
                results = self.service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
                messages.extend(results.get('messages', []))
            return messages
        except Exception as error:
            print(f'An error occurred searching messages: {error}')
            return []

    def get_message_detail(self, message_id):
        """Retrieves full details of a specific message."""
        try:
            return self.service.users().messages().get(userId='me', id=message_id).execute()
        except Exception as error:
            print(f'An error occurred getting message detail: {error}')
            return None
