import json, asyncio
import threading
from uuid import uuid4
from flask import Flask, request, jsonify
from scraper import handle_request

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
        d = json.load(open(f'./data/{id}.json', 'r'))
    except:
        return jsonify({"error": "No data found for the given ID"}), 404

    idx = d.get('index')
    status = d.get('status', 'pending')
    emails = d.get('emails', [])

    if not isinstance(idx, int):
        return jsonify({"error": "No data found for the given ID"}), 404

    if status == 'completed':
        idx = len(emails)
        return jsonify(emails[idx:]), 418

    if idx >= len(emails):
        return jsonify([]), 200

    d['index'] = len(emails)
    json.dump(d, open(f'./data/{id}.json', 'w'))
    return jsonify(emails[idx:]), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
