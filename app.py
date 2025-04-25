from flask import Flask, request
import json
import os
from datetime import datetime
import requests

app = Flask(__name__)

BOT_ID = 'Brendan's Word Counter'
TARGET_NAME = "Brendan O'Bryant"
WORD_LIMIT = 100
STORAGE_FILE = 'word_counts.json'

def load_data():
    if not os.path.exists(STORAGE_FILE):
        return {}
    with open(STORAGE_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f)

def get_today():
    return datetime.utcnow().strftime('%Y-%m-%d')

def count_words(message):
    return len(message.strip().split())

def post_message(text):
    url = 'https://api.groupme.com/v3/bots/post'
    data = {
        'bot_id': BOT_ID,
        'text': text
    }
    requests.post(url, json=data)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    name = data.get('name')
    text = data.get('text', '')

    if name != TARGET_NAME:
        return 'OK', 200

    today = get_today()
    word_count = count_words(text)
    storage = load_data()
    user_data = storage.get(today, {})
    current_total = user_data.get(name, 0)
    new_total = current_total + word_count

    # Update and save
    user_data[name] = new_total
    storage[today] = user_data
    save_data(storage)

    # Create and send response
    words_left = max(0, WORD_LIMIT - new_total)
    response = f"You have sent {new_total} words today. You are {words_left} words away from your daily 100 word limit."
    post_message(response)

    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
