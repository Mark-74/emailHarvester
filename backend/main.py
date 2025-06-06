import json, asyncio
import threading
from uuid import uuid4
from flask import Flask, request, jsonify
from utils.scraper import handle_request
from utils.breaches import is_breached

app = Flask(__name__)

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
    if not id:
        return jsonify({"error": "ID parameter is required"}), 400
    
    try:
        data = json.load(open(f'./data/{id}/status.json', 'r'))
        index = json.load(open(f'./data/{id}/index.json', 'r'))
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

    index = {'secure': secidx, 'predicted': predidx}
    json.dump(index, open(f'./data/{id}/index.json', 'w'))
    return jsonify({'secure': secure, 'predicted': predicted}), 200 if status == 'pending' else 418

@app.route('/api/breach', methods=['POST'])
def breach():
    domain = request.json.get('domain').lower()
    return jsonify({'status': 'breached' if is_breached(domain) else 'safe'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
