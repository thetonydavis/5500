import os
from flask import Flask

app = Flask(__name__)

service_account_info = {
  "type": "service_account",
  "project_id": os.getenv('GCP_PROJECT_ID'),
  "private_key_id": os.getenv('GCP_PRIVATE_KEY_ID'),
  "private_key": os.getenv('GCP_PRIVATE_KEY').replace("\\n", "\n"),
  "client_email": os.getenv('GCP_CLIENT_EMAIL'),
  "client_id": os.getenv('GCP_CLIENT_ID'),
  "auth_uri": os.getenv('GCP_AUTH_URI'),
  "token_uri": os.getenv('GCP_TOKEN_URI'),
  "auth_provider_x509_cert_url": os.getenv('GCP_AUTH_PROVIDER_X509_CERT_URL'),
  "client_x509_cert_url": os.getenv('GCP_CLIENT_X509_CERT_URL')
}

@app.route('/')
def home():
    return "Hello, World!"

if __name__ == '__main__':
    app.run()
