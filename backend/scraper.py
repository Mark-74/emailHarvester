import requests, json, re
from bs4 import BeautifulSoup
from googlesearch import search
from urllib.parse import urlencode

DEPTH_LIMIT = 10

async def handle_request(id: str, domain: str, company: str):
    init_data(id)

    await scrape_dorks(id, domain, company)
    await scrape_website(id, f'https://{domain}', set())

    save_data(id, [], status='completed')

def init_data(id: str):
    data = {
        'status': 'pending',
        'emails': {
            True: [],
            False: []
        },
        'index': 0
    }

    json.dump(data, open(f'./data/{id}.json', 'w'))
    
def save_data(id: str, emails: list[str], predicted: bool = True, status: str = 'pending'):
    with open(f'./data/{id}.json', 'r') as f:
        d = json.load(f)

        values = [v.lower().strip() for v in emails]
        values.extend(d['emails'][predicted])
        values = list(set(values))

        d['emails'][predicted] = values
        d['status'] = status

    json.dump(d, open(f'./data/{id}.json', 'w'))

async def scrape_website(id, url: str, visited: set, depth=0) -> list[str]:
    if depth >= DEPTH_LIMIT or url in visited:
        return

    print(f'Scraping {url} at depth {depth}', flush=True)
    domain = url.split('//')[1]
    visited.add(url)
    email = r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}'

    try:
        r = requests.get(url)
        if r.status_code != 200:
            return
        if r.headers.get('Content-Type') != 'text/html':
            return
    except requests.RequestException:
        return
    
    values = re.findall(email, r.text.lower())
    save_data(id, values)

    # BFS search for more emails
    soup = BeautifulSoup(r.text, 'html.parser')
    for a in soup.find_all(href=True):
        if a['href'].startswith('/'):
            a['href'] = url + a['href']
        if not domain in a['href']:
            continue
        if not a['href'].startswith('http'):
            continue
        if '#' in a['href']:
            a['href'] = a['href'].split('#')[0]

        while a['href'].endswith('/'):
            a['href'] = a['href'][:-1]

        
        assert isinstance(a['href'], str), a['href']
        await scrape_website(id, a['href'], visited, depth + 1)

async def scrape_dorks(id: str, domain: str, company: str) -> list[str]:
    query = f'site:linkedin.com/in "{company}" AND ("email" OR "contact")'
    url = f"https://www.google.com/search?{urlencode({'q': query})}"

    try:
        r = requests.get(url)
        if r.status_code != 200:
            print(f"Failed to fetch dorks for {company}. Status code: {r.status_code}", flush=True)
            return
    except:
        return

    res = search(query, num_results=50)
    values = []
    for url in res:
        data = url.split('/in/')[1].split('-')

        if len(data) < 2:
            continue
        firstname, lastname = data[:2]

        mails = [
            f'{firstname}.{lastname}@{domain}',
            f'{firstname[0]}.{lastname}@{domain}',
            f'{firstname}{lastname}@{domain}',
        ]

        values.extend(mails)
    
    save_data(id, values, predicted=True)

if __name__ == "__main__":
    import asyncio, os
    domain = "cyberloop.it"
    company = "Cyberloop"
    id = os.urandom(16).hex()
    asyncio.run(handle_request(id, domain, company))
    print(f"Scraping completed for {domain} with ID {id}.")
