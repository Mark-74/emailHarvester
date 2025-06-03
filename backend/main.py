import json
from uuid import uuid4
from flask import Flask, request, jsonify, send_file
from scraper import handle_request

app = Flask(__name__)

@app.route('/api/search', methods=['POST'])
async def search():
    domain = request.json.get('domain')

    if not domain:
        return jsonify({"error": "Domain parameter is required"}), 400

    id = str(uuid4())
    handle_request(domain, id)

    return jsonify({'id': id})

@app.route('/api/fetch', methods=['GET'])
def fetch():
    id = request.json.get('id')
    if not id:
        return jsonify({"error": "ID parameter is required"}), 400
    d = json.load(open(f'./data/{id}.json', 'r'))
    
    idx = d.get('index')
    status = d.get('status', 'pending')
    emails = d.get('emails', [])

    if not idx:
        return jsonify({"error": "No data found for the given ID"}), 500
    
    if idx >= len(emails):
        return jsonify([]), 200

    d['index'] = len(emails)
    json.dump(d, open(f'./data/{id}.json', 'w'))
    return jsonify(emails[idx:]), 418 if status != 'pending' else 200

if __name__ == '__main__':
    app.run(debug=True)
