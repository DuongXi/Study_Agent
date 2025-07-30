from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys
import os
from pathlib import Path
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.tool_config import SCOPES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the directory where auth.py is located
AUTH_DIR = Path(__file__).parent
TOKEN_PATH = AUTH_DIR / "token.json"
CRED_PATH = AUTH_DIR / "auth" / "cred.json"

# Xác thực Google Drive
def drive_authenticate():
    try:
        creds = None
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:   
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CRED_PATH), SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        return creds
    except Exception as e:
        logger.error(f"Lỗi xác thực: {str(e)}")
        raise

# Xác thực Google Calendar
def calendar_authenticate(access_token, refresh_token):
  try:
    if not access_token or not refresh_token:
        raise ValueError("Access token and refresh token are required")

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES
    )
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
    return creds
  except Exception as e:
    logger.error(f"Lỗi xác thực: {str(e)}")
    raise
  