from google.cloud import bigquery
from google.oauth2 import service_account
import json
import csv
import argparse
from flask import Flask, request, jsonify

app = Flask(__name__)

import os

service_account_info = {
  "type": "service_account",
  "project_id": os.getenv('GCP_PROJECT_ID'),
  "private_key_id": os.getenv('GCP_PRIVATE_KEY_ID'),
  "private_key": os.getenv('GCP_PRIVATE_KEY').replace("\\n", "\n"),
  "client_email": os.getenv('GCP_CLIENT_EMAIL'),
  ...
}


credentials = service_account.Credentials.from_service_account_info(service_account_info)

# Initialize a BigQuery client
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

@app.route('/run_query', methods=['POST'])
def run_query():
    try:
        ein = request.json.get('ein')
        query = """
        SELECT
            *
        FROM
            `waivz-404004.form_5500_2022.2022 Production`
        WHERE
            ein = @ein
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("ein", "INT64", ein)
            ]
        )
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()

        output = []
        for row in results:
            output.append(dict(row.items()))

        return jsonify(output)
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
