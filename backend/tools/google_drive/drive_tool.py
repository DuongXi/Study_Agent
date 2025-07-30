from googleapiclient.discovery import build
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))
from auth.auth import drive_authenticate


class Drive():
    def __init__(self):
        self.creds = drive_authenticate()

    # Lấy danh sách tất cả các file trong thư mục
    def list_files(self, folder_id):
        service = build('drive', 'v3', credentials=self.creds)
        
        query = f"'{folder_id}' in parents and trashed = false"

        results = service.files().list(
            q=query,
            pageSize=100,
            fields="files(name, id)"
        ).execute()
        items = results.get('files', [])
        
        return items
    
    # Lấy link của file
    def get_file_link(self, file_name, folder_id):
        service = build('drive', 'v3', credentials=self.creds)
        
        query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
        
        results = service.files().list(
            q=query,
            fields="files(webViewLink)"
        ).execute()
        items = results.get('files', [])
        if items:
            return items[0]['webViewLink']
        return None

if __name__ == "__main__":
    drive = Drive()