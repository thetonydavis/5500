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
