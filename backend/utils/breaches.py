import requests

def is_breached(domain: str) -> bool:
    data = requests.get(f'https://api.breachsense.com/stats?s={domain}', headers={'Origin': 'https://breachsense.com'}).json()
    return data.get('emp') > 0 or data.get('usr') > 0
