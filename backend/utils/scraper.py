import requests, json, re
from bs4 import BeautifulSoup
from googlesearch import search
from duckduckgo_search import DDGS
from urllib.parse import urlencode
from pymongo.database import Database
from utils.checker import *
from utils.jsonio import init_data, save_data, load_data

DEPTH_LIMIT = 10

async def handle_request(id: str, domain: str, company: str, db: Database):
    init_data(id, db)

    await scrape_dorks_google(id, domain, company, db)
    await scrape_dorks_duck(id, domain, company, db)
    await scrape_website(id, f'https://{domain}', set(), db)

    if test_tor_connection():
        onions = json.load(open('static.json'))
        for onion in onions:
            await scrape_website(id, onion, set(), db, onion=True)

    smtps = get_mail_from_domain(domain)
    data = load_data(id, db)
    secured = []
    try:
        pattern = verify_pattern(data['emails']['secure'], data['emails']['predicted'])
        if pattern:
            matches = []
            for i in data['emails']['predicted']:
                if re.match(pattern, i.split('@')[0]):
                    matches.append(i)
            
            for smtp in smtps:
                for email in matches:
                    if verify_email(email, smtp):
                        secured.append(email)
        else:
            predicted = data['emails']['predicted'][:3]
            for i in range(len(predicted)):
                found = False
                for smtp in smtps:
                    if verify_email(predicted[i], smtp):
                        secured.extend(data['emails']['predicted'][i::3+i])
                        found = True
                        break
                
                if found:
                    break

    except Exception as e:
        print(f"Error during verification: {e}", flush=True)
        pass
    
    if len(secured) > 0:
        data['emails']['secure'].extend(secured)
    save_data(id, data['emails']['secure'], db, status='completed')


async def scrape_website(id, url: str, visited: set,  db: Database, onion: bool = False, depth: int = 0):
    if depth >= DEPTH_LIMIT or url in visited:
        return

    domain = url.split('//')[1]
    visited.add(url)
    email = r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}'

    try:
        r = requests.get(url, proxies=PROXIES if onion else None, timeout=10)
        if r.status_code != 200:
            return
        if r.headers.get('Content-Type') != 'text/html':
            return
    except requests.RequestException:
        return
    
    values = re.findall(email, r.text.lower())
    save_data(id, values, db)

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
        await scrape_website(id, a['href'], visited, onion=onion, depth=depth + 1)

async def scrape_dorks_google(id: str, domain: str, company: str, db: Database):
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
        try:
            data = url.split('/in/')[1].split('-')
        except:
            continue

        if len(data) < 2:
            continue
        firstname, lastname = data[:2]

        mails = [
            f'{firstname}.{lastname}@{domain}',
            f'{firstname[0]}.{lastname}@{domain}',
            f'{firstname}{lastname}@{domain}',
        ]

        values.extend(mails)
    
    save_data(id, values, db, predicted=True)

async def scrape_dorks_duck(id: str, domain: str, company: str, db: Database):
    query = f'site:linkedin.com/in "{company}" AND ("email" OR "contact")'
    url = f"https://duckduckgo.com/?{urlencode({'q': query})}"

    try:
        r = requests.get(url)
        if r.status_code != 200:
            print(f"Failed to fetch dorks for {company}. Status code: {r.status_code}", flush=True)
            return
    except:
        return

    res = DDGS().text(query, max_results=50)
    values = []
    for url in res:
        try:
            data = url['href'].split('/in/')[1].split('-')
        except:
            continue

        if len(data) < 2:
            continue
        firstname, lastname = data[:2]

        mails = [
            f'{firstname}.{lastname}@{domain}',
            f'{firstname[0]}.{lastname}@{domain}',
            f'{firstname}{lastname}@{domain}',
        ]

        values.extend(mails)
    
    save_data(id, values, db, predicted=True)