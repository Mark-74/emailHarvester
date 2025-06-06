import requests
from datetime import datetime

def is_breached(company: str) -> bool:
    year, month = 2020, 1
    now = datetime.now()
    end_year, end_month = now.year, now.month
    while (year < end_year) or (year == end_year and month <= end_month):
        month_name = datetime(year, month, 1).strftime("%B").lower()

        r = requests.get(f"https://www.breachsense.com/breaches/{year}/{month_name}/")
        print(r.text, flush=True)
        if company in r.text.lower():
            return True

        month += 1
        if month > 12:
            month = 1
            year += 1

    return False