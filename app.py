from flask import Flask, jsonify, Response
import json
import instaloader
import logging
import os
import time
import random
import re

app = Flask(__name__)

SESSION_FILE = "loopstar154_session12"
INSTAGRAM_USERNAME = "loopstar154"
INSTAGRAM_PASSWORD = "Starbuzz6@"
MAX_RETRIES = 3

L = instaloader.Instaloader()
def create_instaloader_instance():
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    L.user_agent = USER_AGENT

    proxies = {
            'http': 'socks5://yoqytafd-6:2dng483b96qx@p.webshare.io:80',
            'https': 'socks5://yoqytafd-6:2dng483b96qx@p.webshare.io:80',
    }
    L.context._session.proxies.update(proxies)


    # try:
    #     with open(SESSION_FILE, 'rb') as session_file:
    #         L.context.load_session_from_file(INSTAGRAM_USERNAME,session_file)
    # except instaloader.exceptions.QueryReturnedNotFoundException:
    #     L.context.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    #     with open(SESSION_FILE, 'wb') as session_file:
    #         L.context.save_session_to_file(session_file)


    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'rb') as session_file:
                L.context.load_session_from_file(INSTAGRAM_USERNAME, session_file)
            
            if not L.context.is_logged_in:
                logging.info("Logging in...")
                L.context.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                logging.info("Logging Done")
                with open(SESSION_FILE, 'wb') as session_file:
                    L.context.save_session_to_file(session_file)
                    logging.info("logged the session")
        else:
            L.context.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            with open(SESSION_FILE, 'wb') as session_file:
                L.context.save_session_to_file(session_file)
    except instaloader.exceptions.QueryReturnedNotFoundException as e:
        logging.error(f"QueryNotFoundException: {e}")
    return L

def create_instaloader_instance1():
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    INSTAGRAM_USERNAME = "loopstar154"
    INSTAGRAM_PASSWORD = "Starbuzz6@"

    L1 = instaloader.Instaloader()    
    L1.user_agent = USER_AGENT
    L1.context.max_connection_attempts = 10
    L1.context.request_timeout = 86400

    try:
        proxies = {
            'http': 'socks5://yoqytafd-6:2dng483b96qx@p.webshare.io:80',
            'https': 'socks5://yoqytafd-6:2dng483b96qx@p.webshare.io:80',
        }
        L1.context._session.proxies.update(proxies)

        L1.context.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

        L1.save_session_to_file('loopstar154_session4')
    except Exception as e:
        print(f"An error occurred: {e}")



def calculate_engagement_rate(username, last_n_posts=10):
    # L = create_instaloader_instance()
    profile = instaloader.Profile.from_username(L.context, username)
    all_posts = list(profile.get_posts())
    total_number_of_posts = len(all_posts)
    number_post = min(last_n_posts, total_number_of_posts)

    if number_post == 0:
        engagement_rate = 0.0
    else:
        posts_consider = all_posts[:number_post]

        total_likes = sum(post.likes for post in posts_consider)
        total_comments = sum(post.comments for post in posts_consider)

        total_interactions = total_likes + total_comments

        if profile.followers == 0:
            engagement_rate = None
        else:
            engagement_rate = (total_interactions / number_post) / profile.followers * 100
    
    time.sleep(random.uniform(1, 3))
    return engagement_rate

def extract_phone_number(bio):
    phone_pattern = re.compile(r'\b\d+[-.\s]?\d+[-.\s]?\d+\b')
    # phone_pattern = re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
    phone_numbers = re.findall(phone_pattern, bio)
    return phone_numbers

def extract_email(bio):
    # email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    email_matches = re.findall(email_pattern, bio)
    return email_matches[0] if email_matches else None

@app.route('/profile/<username>')
def get_instagram_profile(username):
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            L = create_instaloader_instance()
            profile = instaloader.Profile.from_username(L.context, username)
            engagement_rate = round(calculate_engagement_rate(username), 2)
            
            phone_number = extract_phone_number(profile.biography)
            email = extract_email(profile.biography)

            data = {
                'username': profile.username,
                'followees': profile.followees,
                'followers': profile.followers,
                'biography': profile.biography,
                'full_name': profile.full_name,
                'engagement_rate': engagement_rate,
                'phone_number': phone_number,
                'email': email
            }

            response = {
                'success': True,
                'message': 'Data received successfully',
                'data': data
            }
            json_data = json.dumps(response, ensure_ascii=False)
            return Response(json_data, content_type='application/json; charset=utf-8')

        except instaloader.exceptions.ProfileNotExistsException:
            response = {
                'success': False,
                'message': 'Profile not found',
                'data': None
            }
            return jsonify(response)

        except Exception as e:
            logging.error(f"An error occurred while fetching profile: {e}")
            retry_count += 1
            wait_time = 2 ** retry_count  # Exponential backoff: 2^1, 2^2, 2^3, ...
            time.sleep(wait_time)
    
    response = {
        'success': False,
        'message': 'Max retries reached. Unable to fetch profile.',
        'data': None
    }
    return jsonify(response)



if __name__ == '__main__':
    app.run(debug=True, port=5002)
