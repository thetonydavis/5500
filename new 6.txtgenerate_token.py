import os
from google.oauth2 import service_account
import google.auth.transport.requests

# Path to your service account key file
key_file_path = 'C:\drive_d\documents\flask_app_clean\service-account-file.json'

# Load the service account credentials
credentials = service_account.Credentials.from_service_account_file(key_file_path)

# Request object needed to refresh the token
auth_req = google.auth.transport.requests.Request()

# Refresh the token to get a valid one
credentials.refresh(auth_req)

# The token you need to set in Render
token = credentials.token
print("Generated Token:", token)
