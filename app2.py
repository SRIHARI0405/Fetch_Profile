from flask import Flask, jsonify, Response
import json
import instaloader
import logging
import os
import re
import time
import random

app = Flask(__name__)

SESSION_FILE = os.getenv('INSTA_SESSION_FILE', 'loopstar154_session7')
INSTAGRAM_USERNAME = os.getenv('loopstar154')
INSTAGRAM_PASSWORD = os.getenv('Starbuzz6@')
HTTP_PROXY = os.getenv('socks5://yoqytafd-6:2dng483b96qx@p.webshare.io:80')
HTTPS_PROXY = os.getenv('socks5://yoqytafd-6:2dng483b96qx@p.webshare.io:80')

def create_instaloader_instance():
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    L = instaloader.Instaloader()
    L.user_agent = USER_AGENT  

    try:
        if os.path.exists(SESSION_FILE):
            L.load_session_from_file(INSTAGRAM_USERNAME, SESSION_FILE)
            if not L.context.is_logged_in:
                logging.info("Logging in...")
                try:
                    L.context.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                    logging.info("Login successful")
                    with open(SESSION_FILE, 'wb') as session_file:
                        L.context.save_session_to_file(session_file)
                        logging.info("Session saved")
                except instaloader.exceptions.InstaloaderException as e:
                    logging.error(f"Login error: {e}")
        else:
            L.context.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            L.save_session_to_file(SESSION_FILE)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    proxies = {
        'http': HTTP_PROXY,
        'https': HTTPS_PROXY,
    }
    L.context._session.proxies.update(proxies)
    return L

def calculate_engagement_rate(username, last_n_posts=10):
    L = create_instaloader_instance()
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

# def calculate_engagement_rate(username, last_n_posts=10):
#     L = create_instaloader_instance()
#     profile = instaloader.Profile.from_username(L.context, username)
#     posts = profile.get_posts()

#     total_likes = total_comments = 0
#     for post in posts:
#         if last_n_posts <= 0:
#             break
#         total_likes += post.likes
#         total_comments += post.comments
#         last_n_posts -= 1
#         time.sleep(random.uniform(1, 3))  # Delay to mimic human behavior and respect rate limits

#     total_interactions = total_likes + total_comments
#     number_of_posts = profile.mediacount

#     engagement_rate = (total_interactions / 10) / profile.followers * 100
#     return engagement_rate


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
    L = instaloader.Instaloader()
    try:
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
        return jsonify({'success': False, 'message': 'Profile not found', 'data': None})

    except Exception as e:
        logging.error(f"An error occurred while fetching profile: {e}")
        return jsonify({'success': False, 'message': str(e), 'data': None})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
