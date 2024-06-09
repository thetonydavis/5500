from flask import Flask, request, jsonify
import os
from google.cloud import bigquery
from google.oauth2 import service_account

app = Flask(__name__)

# Ensure your credentials are set up correctly
service_account_info = {
    "type": "service_account",
    "project_id": "waivz-404004",
    "private_key_id": os.getenv('GCP_PRIVATE_KEY_ID'),
    "private_key": os.getenv('GCP_PRIVATE_KEY').replace("\\n", "\n"),
    "client_email": os.getenv('GCP_CLIENT_EMAIL'),
    "client_id": "101013593038616372404",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv('GCP_CLIENT_X509_CERT_URL'),
}
credentials = service_account.Credentials.from_service_account_info(service_account_info)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

@app.route('/bigquery/company_name_state_lookup', methods=['POST'])
def company_name_state_lookup():
    data = request.get_json()
    company_name = data.get('company_name')
    employer_state = data.get('employer_state')
    if not company_name or not employer_state:
        return jsonify({"error": "company_name and employer_state are required"}), 400

    query = """
    SELECT * FROM `waivz-404004.form_5500_2022.Company_Name_State_Lookup`
    WHERE CONTAINS_SUBSTR(company_name, @company_name) AND employer_state = @employer_state
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("company_name", "STRING", company_name),
            bigquery.ScalarQueryParameter("employer_state", "STRING", employer_state),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    results = [dict(row) for row in query_job.result()]
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

