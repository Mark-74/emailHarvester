import requests, re
from bs4 import BeautifulSoup
from googlesearch import search
from urllib.parse import urlencode

def scrape_website(url: str) -> list[str]:
    email = r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}'
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return []
        if r.headers.get('Content-Type') != 'text/html':
            return []
    except requests.RequestException:
        return []
    values : list[str] = re.findall(email, r.text.lower())
    # soup = BeautifulSoup(r.text, 'html.parser')
    # for a in tqdm(soup.find_all('a', href=True), desc=f"Scraping {url}"):
    #     values += scrape_website(a['href'])
    
    values = list(set(values))
    values = [v.lower().strip() for v in values] 

    return values

def scrape_dorks(domain: str) -> list[str]:
    query = f"site:{domain} intext:@{domain}"
    url = f"https://google.co.in/search?{urlencode({'q': query})}"

    try:
        r = requests.get(url)
        if r.status_code != 200:
            return []
    except:
        return []

    res = search(query, num_results=10) 
    values = []
    for url in res:
        if domain not in url:
            continue
        values += scrape_website(url)

    return values

if __name__ == "__main__":
    domain = "cyberloop.it"
    results = scrape_dorks(domain)
    print(results)