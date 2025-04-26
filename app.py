from flask import Flask, request
import json
import os
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

# PERSONALIZE THIS: Replace with your bot ID
BOT_ID = 'dae4f30bebc8f7e5334637fea1'

# Brendan's exact GroupMe name
TARGET_NAME = "Brendan O'Bryant"

# This file stores timestamps of Brendan's messages
STORAGE_FILE = 'timestamps.json'


# === Utility Functions ===

def load_data():
    if not os.path.exists(STORAGE_FILE):
        return {}
    with open(STORAGE_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f)

def post_message(text):
    url = 'https://api.groupme.com/v3/bots/post'
    data = {
        'bot_id': BOT_ID,
        'text': text
    }
    response = requests.post(url, json=data)
    if response.status_code != 202:
        print(f"Failed to send message: {response.status_code} - {response.text}")

def get_current_timestamp():
    return datetime.utcnow().timestamp()


# === Webhook ===

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Received data:", data)

    if data.get('sender_type') == 'bot':
        return 'OK', 200

    name = data.get('name')

    if name != TARGET_NAME:
        return 'OK', 200

    current_time = get_current_timestamp()
    storage = load_data()

    # Load Brendan's past timestamps
    timestamps = storage.get(TARGET_NAME, [])

    # Keep only timestamps within the last 60 seconds
    one_minute_ago = current_time - 60
    timestamps = [ts for ts in timestamps if ts >= one_minute_ago]

    # Add current message
    timestamps.append(current_time)
    storage[TARGET_NAME] = timestamps
    save_data(storage)

    # Check how many messages within last minute
    message_count = len(timestamps)
    print(f"Message count in last minute: {message_count}")

    # Send warnings
    if message_count == 2:
        post_message("Slow down Brendan")
    elif message_count == 3:
        post_message("I said slow down!")
    elif message_count == 4:
        post_message("TAKE A BREAK AND TOUCH GRASS")
    elif message_count == 5:
        post_message("Alright that's it. Pastor Lucas, it's time to kick him.")

    return 'OK', 200


# === Start Server ===

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
