import asyncio
import threading, os
from pymongo import MongoClient
from uuid import uuid4
from flask import Flask, request, jsonify
from utils.scraper import handle_request
from utils.breaches import is_breached

MONGO_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME', 'root')
MONGO_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD', 'password')

app = Flask(__name__)
db = MongoClient(f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@mongodb:27017/")['emailharvester']

def run_async_background(coro):
    def runner():
        asyncio.run(coro)
    threading.Thread(target=runner, daemon=True).start()

@app.route('/api/search', methods=['POST'])
async def search():
    company = request.json.get('company')
    domain = request.json.get('domain')

    if not domain or not company:
        return jsonify({"error": "Domain and company parameters are required"}), 400
    if not isinstance(domain, str) or not isinstance(company, str):
        return jsonify({"error": "Domain and company parameters must be strings"}), 400

    id = str(uuid4())
    run_async_background(handle_request(id, domain, company))

    return jsonify({'id': id})

@app.route('/api/fetch', methods=['GET'])
def fetch():
    id = request.args.get('id')
    # TODO: add index in frontend request thanks to sessions
    index = request.args.get('index', {'secure': 0, 'predicted': 0})

    if not id or not isinstance(id, str):
        return jsonify({"error": "ID parameter is required"}), 400
    if not index or not isinstance(index, dict):
        return jsonify({"error": "Index parameter must be a non-negative integer"}), 400
    
    try:
        data: dict[str, any] = db['results'].find_one({"id": id})
    except:
        return jsonify({"error": "No data found for the given ID"}), 404

    secidx, predidx = index.values()
    status = data.get('status', 'pending')
    emails = data.get('emails', {'secure': [], 'predicted': []})

    predicted, secure = [], []
    if secidx < len(emails['secure']) :
        secure = emails['secure'][secidx:]
        secidx = len(emails['secure'])
    if predidx < len(emails['predicted']):
        predicted = emails['predicted'][predidx:]
        predidx = len(emails['predicted'])

    # TODO: handle response in frontend by updating index and giving real frontend the data
    return jsonify({
        'index': {'secure': secidx, 'predicted': predidx},
        'data': {'secure': secure, 'predicted': predicted}
    }), 200 if status == 'pending' else 418

@app.route('/api/breach', methods=['POST'])
def breach():
    domain = request.json.get('domain').lower()
    if not domain or not isinstance(domain, str):
        return jsonify({"error": "Domain parameter is required"}), 400
    
    data = db['breaches'].find_one({"domain": domain})
    if not data:
        status = 'breached' if is_breached(domain) else 'safe'
        db['breaches'].insert_one({"domain": domain, "status": status})
        return jsonify({'status': status})
    return jsonify({'status': data['status']})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
