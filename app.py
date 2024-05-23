import os
import logging
from flask import Flask, jsonify, request
from google.oauth2 import service_account
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

def standardize_state(state_input):
    state_input_upper = state_input.upper().strip()
    state_abbreviations = {
        "ALABAMA": "AL", "ALASKA": "AK", "ARIZONA": "AZ", "ARKANSAS": "AR",
        "CALIFORNIA": "CA", "COLORADO": "CO", "CONNECTICUT": "CT", "DELAWARE": "DE",
        "FLORIDA": "FL", "GEORGIA": "GA", "HAWAII": "HI", "IDAHO": "ID",
        "ILLINOIS": "IL", "INDIANA": "IN", "IOWA": "IA", "KANSAS": "KS",
        "KENTUCKY": "KY", "LOUISIANA": "LA", "MAINE": "ME", "MARYLAND": "MD",
        "MASSACHUSETTS": "MA", "MICHIGAN": "MI", "MINNESOTA": "MN", "MISSISSIPPI": "MS",
        "MISSOURI": "MO", "MONTANA": "MT", "NEBRASKA": "NE", "NEVADA": "NV",
        "NEW HAMPSHIRE": "NH", "NEW JERSEY": "NJ", "NEW MEXICO": "NM", "NEW YORK": "NY",
        "NORTH CAROLINA": "NC", "NORTH DAKOTA": "ND", "OHIO": "OH", "OKLAHOMA": "OK",
        "OREGON": "OR", "PENNSYLVANIA": "PA", "RHODE ISLAND": "RI", "SOUTH CAROLINA": "SC",
        "SOUTH DAKOTA": "SD", "TENNESSEE": "TN", "TEXAS": "TX", "UTAH": "UT",
        "VERMONT": "VT", "VIRGINIA": "VA", "WASHINGTON": "WA", "WEST VIRGINIA": "WV",
        "WISCONSIN": "WI", "WYOMING": "WY"
    }
    return state_abbreviations.get(state_input_upper, state_input_upper)

def validate_and_sanitize_ein(ein):
    if '-' in ein:
        ein = ein.replace('-', '')
    if not ein.isdigit() or not (5 <= len(ein) <= 9):
        raise ValueError("EIN must be a numeric string of 5 to 9 digits.")
    return ein

def format_output(data):
    return {
        "General Plan Information": [
            {"Company Name": data.get("Company_Name", "<V>")},
            {"Plan Name": data.get("Plan_Name", "<V>")},
            {"Effective Date": data.get("Effective_Date", "<V>")},
            {"Plan Year Begin Date": data.get("Plan_Year_Begin_Date", "<V>")},
            {"Plan Year End Date": data.get("Plan_Year_End_Date", "<V>")},
            {"Employer Match YN": data.get("Employer_Match_YN", "<V>")},
            {"PCC Codes": data.get("PCC_Codes", "<V>")},
            {"5500 Link": data.get("_5500_link", "<V>")},
            {"EIN": data.get("EIN", "<V>")},
            {"Age of Plan": data.get("Age_of_Plan", "<V>")},
        ],
        "Financial Information": [
            {"Plan Assets (BOY)": data.get("Assets_BOY", "<V>")},
            {"Plan Assets (EOY)": data.get("Assets_EOY", "<V>")},
            {"Participant Contributions": data.get("Contributions_Participants_EOY", "<V>")},
            {"Employer Contributions": data.get("Contributions_Employer_EOY", "<V>")},
            {"Average Account Balance": data.get("Average_Account_Balance", "<V>")},
        ],
        "Participant Information": [
            {"Participants - Active - EOY": data.get("Active_Participants_EOY", "<V>")},
            {"Average Account Balance": data.get("Average_Account_Balance", "<V>")},
        ],
        "Employer Information": [
            {"Company Name": data.get("Company_Name", "<V>")},
            {"Employer Street": data.get("Employer_Street", "<V>")},
            {"Employer City": data.get("Employer_City", "<V>")},
            {"Employer State": data.get("Employer_State", "<V>")},
            {"Employer Zip": data.get("Employer_Zip", "<V>")},
            {"Employer Telephone": data.get("Employer_Telephone", "<V>")},
            {"Business (NAICS) Code": data.get("Business_Code", "<V>")},
        ],
        "Compliance and Administrative Information": [
            {"Admin Signed Name": data.get("Admin_Signed_Name", "<V>")},
            {"Admin Signed Date": data.get("Admin_Signed_Date", "<V>")},
            {"Fidelity Bond YN": data.get("Fidelity_Bond_YN", "<V>")},
            {"Loss Due to Fraud YN": data.get("Loss_Due_to_Fraud_YN", "<V>")},
            {"Failure to Transmit Contributions YN": data.get("Fail_to_Transmit_Contributions_YN", "<V>")},
            {"Corrective Distribution YN": data.get("Corrective_Distribution_YN", "<V>")},
            {"Failure Provide Benefits YN": data.get("Failure_Provide_Benefits_YN", "<V>")},
            {"Party in Interest YN": data.get("Party_in_Interest_YN", "<V>")},
        ],
        "Service Provider Information": [
            {"Provider Name": data.get("PROVIDER_NAME", "<V>")},
            {"Provider Relation": data.get("PROVIDER_RELATION", "<V>")},
            {"Provider Direct Comp": data.get("PROVIDER_DIRECT_COMP", "<V>")},
            {"Provider Indirect Comp": data.get("PROVIDER_INDIRECT_COMP", "<V>")},
        ],
    }

@app.route('/')
def home():
    logger.debug("Home route accessed")
    return 'Flask Application is Running'

@app.route('/hello')
def hello():
    logger.debug("Hello route accessed")
    return 'Hello, World!'

@app.route('/search/ein', methods=['GET'])
def search_by_ein():
    try:
        ein = request.args.get('ein')
        logger.debug(f"Received EIN: {ein}")
        if not ein:
            logger.debug("EIN not provided")
            return jsonify({"error": "EIN is required"}), 400
        ein = validate_and_sanitize_ein(ein)
        logger.debug(f"Sanitized EIN: {ein}")
        query = """
        SELECT TO_JSON_STRING(STRUCT(
            Plan_Year_Begin_Date, EIN, Effective_Date, Company_Name, Employer_Street,
            Employer_City, Employer_State, Employer_Zip, Employer_Telephone, Business_Code,
            Admin_Signed_Name, Admin_Signed_Date, Participants_BOY, Active_Participants_EOY,
            PCC_Codes, Contributions_Employer_EOY, Contributions_Participants_EOY, Assets_BOY,
            Assets_EOY, Corrective_Distribution_YN, Corrective_Distribution_Amt,
            Fail_to_Transmit_Contributions_YN, Fail_to_Transmit_Contributions_Amt,
            Party_in_Interest_YN, Party_in_Interest_Amt, Fidelity_Bond_YN, Fidelity_Bond_Amt,
            Loss_Due_to_Fraud_YN, Loss_Due_to_Fraud_Amt, Broker_Fees_Paid_YN,
            Broker_Fees_Paid_Amt, Failure_Provide_Benefits_YN, Failure_Provide_Benefits_Amt,
            Terminated_Plan_YN, PROVIDER_NAME, PROVIDER_RELATION, PROVIDER_DIRECT_COMP,
            PROVIDER_INDIRECT_COMP, _5500_link, Plan_Name
        )) AS formatted_json
        FROM `waivz-404004.form_5500_2022.2022 Production`
        WHERE EIN = @searchValue
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("searchValue", "STRING", ein)
            ]
        )
        logger.debug(f"Executing query: {query}")
        query_job = client.query(query, job_config=job_config)
        results = [dict(row) for row in query_job.result()]
        logger.debug(f"Query Results: {results}")
        formatted_results = [format_output(json.loads(result['formatted_json'])) for result in results]
        logger.debug(f"Formatted Results: {formatted_results}")
        return jsonify(formatted_results)
    except ValueError as ve:
        logger.error(f"ValueError: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error querying BigQuery: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/search/plan-name', methods=['GET'])
def search_by_plan_name():
    try:
        plan_name = request.args.get('plan_name')
        state = request.args.get('state')
        logger.debug(f"Received Plan Name: {plan_name}, State: {state}")
        if not plan_name or not state:
            logger.debug("Plan Name or State not provided")
            return jsonify({"error": "Plan Name and State are required"}), 400
        state = standardize_state(state)
        logger.debug(f"Standardized State: {state}")
        query = """
        SELECT TO_JSON_STRING(STRUCT(
            Plan_Year_Begin_Date, EIN, Effective_Date, Company_Name, Employer_Street,
            Employer_City, Employer_State, Employer_Zip, Employer_Telephone, Business_Code,
            Admin_Signed_Name, Admin_Signed_Date, Participants_BOY, Active_Participants_EOY,
            PCC_Codes, Contributions_Employer_EOY, Contributions_Participants_EOY, Assets_BOY,
            Assets_EOY, Corrective_Distribution_YN, Corrective_Distribution_Amt,
            Fail_to_Transmit_Contributions_YN, Fail_to_Transmit_Contributions_Amt,
            Party_in_Interest_YN, Party_in_Interest_Amt, Fidelity_Bond_YN, Fidelity_Bond_Amt,
            Loss_Due_to_Fraud_YN, Loss_Due_to_Fraud_Amt, Broker_Fees_Paid_YN,
            Broker_Fees_Paid_Amt, Failure_Provide_Benefits_YN, Failure_Provide_Benefits_Amt,
            Terminated_Plan_YN, PROVIDER_NAME, PROVIDER_RELATION, PROVIDER_DIRECT_COMP,
            PROVIDER_INDIRECT_COMP, _5500_link, Plan_Name
        )) AS formatted_json
        FROM `waivz-404004.form_5500_2022.2022 Production`
        WHERE REGEXP_CONTAINS(Plan_Name, '(?i)' || @planName)
          AND Employer_State = @state
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("planName", "STRING", plan_name),
                bigquery.ScalarQueryParameter("state", "STRING", state)
            ]
        )
        logger.debug(f"Executing query: {query}")
        query_job = client.query(query, job_config=job_config)
        results = [dict(row) for row in query_job.result()]
        logger.debug(f"Query Results: {results}")
        formatted_results = [format_output(json.loads(result['formatted_json'])) for result in results]
        logger.debug(f"Formatted Results: {formatted_results}")
        return jsonify(formatted_results)
    except Exception as e:
        logger.error(f"Error querying BigQuery: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
