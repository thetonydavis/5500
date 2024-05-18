import os
from flask import Flask, jsonify

app = Flask(__name__)

# Check and load environment variables
gcp_private_key = os.getenv('GCP_PRIVATE_KEY')
if not gcp_private_key:
    raise EnvironmentError("GCP_PRIVATE_KEY environment variable not set")

service_account_info = {
    "type": "service_account",
    "project_id": os.getenv('GCP_PROJECT_ID', 'default_project_id'),
    "private_key_id": os.getenv('GCP_PRIVATE_KEY_ID', 'default_private_key_id'),
    "private_key": gcp_private_key.replace("\\n", "\n"),
    "client_email": os.getenv('GCP_CLIENT_EMAIL', 'default_client_email'),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv('GCP_CLIENT_X509_CERT_URL', 'default_client_x509_cert_url')
}

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/token')
def token():
    try:
        token = os.getenv('YOUR_TOKEN_VARIABLE')
        if not token:
            raise ValueError("Token not found in environment variables")
        return jsonify({"token": token})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
