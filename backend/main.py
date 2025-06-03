#!/usr/env/python3
from flask import Flask, request, jsonify
from scraper import scrape_website, scrape_dorks

app = Flask(__name__)

@app.route('/api/search', methods=['GET'])
def search():
    domain = request.args.get('domain')
    if not domain:
        return jsonify({"error": "Domain parameter is required"}), 400
    
    results = []
    results.extend(scrape_website(domain))
    results.extend(scrape_dorks(domain))

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
