from pymongo.database import Database

def init_data(id: str, db: Database):
    db['results'].insert_one({
        'id': id,
        'status': 'pending',
        'emails': {
            'secure': [],
            'predicted': []
        }
    })

def save_data(id: str, emails: list[str], db: Database, predicted: bool = False, status: str = 'pending'):
    predicted = 'predicted' if predicted else 'secure'
    data = db['results'].find_one({"id": id})
    values = []
    if data:
        values = [v.lower().strip() for v in data['emails'][predicted]]
    values.extend(emails)
    values = list(dict.fromkeys(values))

    db['results'].update_one({"id": id}, {"$set": {f'emails.{predicted}': values, 'status': status}})


def load_data(id: str, db: Database):
    return db['results'].find_one({"id": id})