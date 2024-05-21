import requests
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'C:\Drive_D\Documents\Waivz\Service_account_key_bg.json'

# Authenticate and get an access token
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

credentials.refresh(Request())
access_token = credentials.token

# Set the request URL and headers
url = "https://bigquery.googleapis.com/bigquery/v2/projects/waivz-404004/queries"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Define the query payload
data = {
    "query": "SELECT FORMAT('%T', STRUCT(Plan_Year_Begin_Date, EIN, Effective_Date, CONCAT('\"', REPLACE(Company_Name, '\"', '\"\"'), '\"'), Employer_Street, Employer_City, Employer_State, Employer_Zip, Employer_Telephone, Business_Code, CONCAT('\"', REPLACE(Admin_Signed_Name, '\"', '\"\"'), '\"'), Admin_Signed_Date, Participants_BOY, Active_Participants_EOY, PCC_Codes, Contributions_Employer_EOY, Contributions_Participants_EOY, Assets_BOY, Assets_EOY, Corrective_Distribution_YN, Corrective_Distribution_Amt, Fail_to_Transmit_Contributions_YN, Fail_to_Transmit_Contributions_Amt, Party_in_Interest_YN, Party_in_Interest_Amt, Fidelity_Bond_YN, Fidelity_Bond_Amt, Loss_Due_to_Fraud_YN, Loss_Due_to_Fraud_Amt, Broker_Fees_Paid_YN, Broker_Fees_Paid_Amt, Failure_Provide_Benefits_YN, Failure_Provide_Benefits_Amt, Terminated_Plan_YN, PROVIDER_NAME, PROVIDER_RELATION, PROVIDER_DIRECT_COMP, PROVIDER_INDIRECT_COMP, CONCAT('\"', REPLACE(_5500_link, '\"', '\"\"'), '\"'), CONCAT('\"', REPLACE(Plan_Name, '\"', '\"\"'), '\"'))) AS formatted_csv FROM `waivz-404004.form_5500_2022.2022_Production` WHERE EIN = @ein",
    "useLegacySql": false,
    "parameterMode": "NAMED",
    "queryParameters": [
        {
            "name": "ein",
            "parameterType": {
                "type": "STRING"
            },
            "parameterValue": {
                "value": "412088193"
            }
        }
    ]
}

# Make the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Print the response
print(response.status_code)
print(response.json())
