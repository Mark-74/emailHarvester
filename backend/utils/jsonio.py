import os, json

def init_data(id: str):
    os.makedirs(f'/app/data/{id}', exist_ok=True)

    data = {
        'status': 'pending',
        'emails': {
            'secure': [],
            'predicted': []
        }
    }

    json.dump(data, open(f'/app/data/{id}/status.json', 'w'))

    data = {
        'secure': 0,
        'predicted': 0
    }
    json.dump(data, open(f'/app/data/{id}/index.json', 'w'))

def save_data(id: str, emails: list[str], predicted: bool = False, status: str = 'pending'):
    predicted = 'predicted' if predicted else 'secure'
    with open(f'/app/data/{id}/status.json', 'r') as f:
        d = json.load(f)

        values = [v.lower().strip() for v in d['emails'][predicted]]
        values.extend(emails)
        values = list(dict.fromkeys(values))

        d['emails'][predicted] = values
        d['status'] = status

    json.dump(d, open(f'/app/data/{id}/status.json', 'w'))

def load_data(id: str):
    try:
        with open(f'/app/data/{id}/status.json', 'r') as f:
            data = json.load(f)
        with open(f'/app/data/{id}/index.json', 'r') as f:
            index = json.load(f)
    except:
        return None, None

    return data, index