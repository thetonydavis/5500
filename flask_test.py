import os  # Importing the os module
import logging
from flask import Flask, jsonify, request
from google.oauth2 import service_account
from google.cloud import bigquery

# Create the Flask application object
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check and load environment variables
gcp_private_key = os.getenv('GCP_PRIVATE_KEY')
if not gcp_private_key:
    logger.error("GCP_PRIVATE_KEY environment variable not set")
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

try:
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
except Exception as e:
    logger.error(f"Error initializing BigQuery client: {str(e)}")
    raise e

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/bigquery', methods=['POST'])
def bigquery_query():
    try:
        data = request.get_json()
        logger.info(f"Received data: {data}")
        ein = data.get('ein')
        if not ein:
            raise ValueError("EIN not provided in the request")

        # Correcting the table name with backticks to handle the space
        query = """
            SELECT TO_JSON_STRING(STRUCT(
                Plan_Year_Begin_Date, 
                EIN, 
                Effective_Date, 
                Company_Name, 
                Employer_Street, 
                Employer_City, 
                Employer_State, 
                Employer_Zip, 
                Employer_Telephone, 
                Business_Code, 
                Admin_Signed_Name, 
                Admin_Signed_Date, 
                Participants_BOY, 
                Active_Participants_EOY, 
                PCC_Codes, 
                Contributions_Employer_EOY, 
                Contributions_Participants_EOY, 
                Assets_BOY, 
                Assets_EOY, 
                Corrective_Distribution_YN, 
                Corrective_Distribution_Amt, 
                Fail_to_Transmit_Contributions_YN, 
                Fail_to_Transmit_Contributions_Amt, 
                Party_in_Interest_YN, 
                Party_in_Interest_Amt, 
                Fidelity_Bond_YN, 
                Fidelity_Bond_Amt, 
                Loss_Due_to_Fraud_YN, 
                Loss_Due_to_Fraud_Amt, 
                Broker_Fees_Paid_YN, 
                Broker_Fees_Paid_Amt, 
                Failure_Provide_Benefits_YN, 
                Failure_Provide_Benefits_Amt, 
                Terminated_Plan_YN, 
                PROVIDER_NAME, 
                PROVIDER_RELATION, 
                PROVIDER_DIRECT_COMP, 
                PROVIDER_INDIRECT_COMP, 
                _5500_link, 
                Plan_Name
            )) AS formatted_json 
            FROM `waivz-404004.form_5500_2022`.`2022 Production`
            WHERE EIN = CAST(@ein AS INT64)
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("ein", "STRING", ein)
            ]
        )

        query_job = client.query(query, job_config=job_config)
        results = [dict(row) for row in query_job.result()]

        return jsonify(results)
    except ValueError as ve:
        logger.error(f"ValueError: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error querying BigQuery: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/custom-query', methods=['POST'])
def custom_query():
    try:
        data = request.get_json(silent=True)
        logger.info(f"Received custom query: {data}")
        query = data.get('query') if data else None

        if not query:
            return jsonify({"error": "No query provided"}), 400

        query_job = client.query(query)  # Make sure the query is secure and valid
        results = query_job.result()  # Waits for job to complete

        # Convert results to a list of dicts to send back
        rows = [dict(row) for row in results]
        return jsonify(rows)
    except Exception as e:
        logger.error(f"Error querying BigQuery: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
