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
        token = os.getenv('ya29.c.c0AY_VpZidQaNUBEbE7OjLy0zHwtS7VTx5mEImTA-mqzNQRLFi8ZXb6BheCW7c4a1xnKpO_qYxrlR6Bhfo8BIxbdpEx-xgWcgKZ1H8Q6VK_NTXa0WmGlc8ujnNsxtPUlJBVqs-15gvQ9Ia82b3OXsbMhKh9Ksz5HcTGURY0esHPmqVuXM87WZG1Ly_JfiVOAbzPaUHZj_LL_l2sXAYais7C3Ulr4RFGLPsFlcKdclz9FuS9cOLCnykXuaDiJst5wpCihoa4IIM1YvoPVPx6JH2BCejCO8cR5mstokylrCGEOal6wqOELw5wSqhKi2xRROGwRBIGBkUUAzQTC_cUT1JSCwhnFlLSZYhCwDPzxsMHR4nBhZJBVST_ecH384P3hRBR4l-ZXlBfJSBVly4S-hhe1i2v96Jvy_3kXS_cereFQXr6-xtzFRmwnfaQf2pUtxyjIOxyaU-Zzk1-Mhjciicx409gSqM5JZBf6SSYVSMVo0R3_g_a9fVm4mQ4yVSfYfSas2oXZXZecSyd-hvcRZIRXfVkcXfq6gv5sM6Wbzl3XR4fMl0whvfb7sR7jvyB--Rzc9JoIf9X_fQipo8xcUXiwnU0FmQZv3u2ft8bz8MOoRZ3kek71m0X-jSmUv7-aOy6MZoS2dvcXyUUo9q9ca9-cqd7MVfsltIb2W9ob7X2iV0j1ytMtyvtcdby8o4F-zpYglOrg0V_F-tyFemf5rOltFk5ft7eouQ2FgQ8nWVapnQQ5oZUyka5rxbMUQVyqtZbtr4QR10qXsRvzjfV7ob6edZ3UZ6QOIJU93maw_4WBn9eum6qfWWhJwO6Ohko_I72o4l2vb1mIt3hO9RqWrBeFthxgrkBlVI1sFn6BWObeY51FXrmmpRIWvnJoIhz4-qkYQxl8JZYs5ZwZfWfbh2k4B24g5pFjWR1b5lwQywSS6fvuvmYwrrbIqQl1MXwuVwhX-ry5JhBjX03pbItsikwiVvWfJ1VkvXJw181F_304l1qr67yjyf0kd')
        if not token:
            raise ValueError("Token not found in environment variables")
        return jsonify({"token": token})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
