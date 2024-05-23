import os
import logging
from flask import Flask, jsonify, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return 'Flask Application is Running'

@app.route('/hello')
def hello():
    return 'Hello, World!'

@app.route('/search/ein', methods=['GET'])
def search_by_ein():
    ein = request.args.get('ein')
    logger.info(f"Received EIN: {ein}")
    if not ein:
        return jsonify({"error": "EIN is required"}), 400
    return jsonify({"message": "EIN route works", "ein": ein})

@app.route('/search/plan-name', methods=['GET'])
def search_by_plan_name():
    plan_name = request.args.get('plan_name')
    state = request.args.get('state')
    logger.info(f"Received Plan Name: {plan_name}, State: {state}")
    if not plan_name or not state:
        return jsonify({"error": "Plan Name and State are required"}), 400
    return jsonify({"message": "Plan Name route works", "plan_name": plan_name, "state": state})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
