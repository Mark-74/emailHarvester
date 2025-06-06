import requests

def is_breached(domain: str) -> bool:
    return not 'No Data Breach Detected' in requests.get(f'https://www.breachsense.com/check-your-exposure/?domain={domain}').text