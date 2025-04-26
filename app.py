from flask import Flask, request
import json
import os
from datetime import datetime
import requests

app = Flask(__name__)

# PERSONALIZE THIS: Replace with your actual bot ID from https://dev.groupme.com/bots
BOT_ID = "Brendan's Word Counter"

# Name must match EXACTLY as it appears in GroupMe messages
TARGET_NAME = "Brendan O'Bryant"
WORD_LIMIT = 100

# This file stores daily word counts
STORAGE_FILE = 'word_counts.json'


# === Utility Functions ===

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
    response = requests.post(url, json=data)
    if response.status_code != 202:
        print(f"Failed to send message: {response.status_code} - {response.text}")


# === Webhook ===

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    # GroupMe will also POST messages sent by your bot — ignore those
    if data.get('sender_type') == 'bot':
        return 'OK', 200

    name = data.get('name')
    text = data.get('text', '')

    # Only track messages from Brendan
    if name != TARGET_NAME:
        return 'OK', 200

    today = get_today()
    word_count = count_words(text)
    storage = load_data()

    # Update daily word count
    if today not in storage:
        storage[today] = {}

    current_total = storage[today].get(name, 0)
    new_total = current_total + word_count
    storage[today][name] = new_total
    save_data(storage)

    words_left = max(0, WORD_LIMIT - new_total)
    response_text = (
        f"You have sent {new_total} words today. "
        f"You are {words_left} words away from your daily 100 word limit."
    )

    post_message(response_text)

    return 'OK', 200


# === Start Server ===

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
