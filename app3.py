from flask import Flask, jsonify
from instagrapi import Client
import time
import os

app = Flask(__name__)

proxy = "socks5://yoqytafd-6:2dng483b96qx@p.webshare.io:80"
session_file = 'session-loop.json'
cl = Client(proxy=proxy)

if os.path.exists(session_file):
    cl.load_settings(session_file)
else:
    username = 'loopstar154'
    password = 'Starbuzz6@'
    login_response = cl.login(username, password)

    if login_response:
        login_response = cl.last_response

def return_profile(account_name):
    max_retries = 3
    base_delay = 5

    for retry_number in range(1, max_retries + 1):
        try:
            profile_info = cl.user_info_by_username(account_name)
            return profile_info
        except Exception as e:
            if "429" in str(e):
                if login_response is not None:
                    rate_limit_remaining = int(login_response.headers.get('x-ratelimit-remaining', 0))
                    rate_limit_reset = int(login_response.headers.get('x-ratelimit-reset', 0))
                    delay_seconds = max(1, rate_limit_reset - int(time.time())) if rate_limit_remaining == 0 else 0
                    print(f"Rate limit exceeded. Retrying in {delay_seconds} seconds (Retry {retry_number}/{max_retries}).")
                    time.sleep(delay_seconds)
                else:
                    print("Login response is None. Exiting.")
                    break
            else:
                print(f"Unexpected error: {e}. Exiting.")
                break

    print("Max retries reached. Exiting.")
    return None

@app.route('/get_profile/<username>')
def get_profile(username):
    profile_info = return_profile(username)
    if profile_info is not None:
        return jsonify(profile_info)
    else:
        return jsonify({"error": "Error retrieving profile."})

if __name__ == '__main__':
    app.run(debug=True)
