import time
from flask import Flask, jsonify, Response
import json
from instagrapi import Client
from instagrapi.types import User
import re  

app = Flask(__name__)

# Load Instagram credentials from a secure location (e.g., environment variables)
INSTAGRAM_USERNAME = 'loopstar154'
INSTAGRAM_PASSWORD = 'Starbuzz6@'

# Initialize Instagram client
proxy = "socks5://yoqytafd-6:2dng483b96qx@p.webshare.io:80"
cl = Client(proxy=proxy)

try:
    cl.load_settings('session-loop.json')
    cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
except Exception as e:
    print(f"Instagram login failed: {e}")

# def calculate_engagement_rate(username, last_n_posts=10):
#   user_id = cl.user_id_from_username(username)
#   posts = cl.user_medias(user_id)
#   total_likes = 0
#   total_comments = 0
#   post_count = min(last_n_posts, len(posts))
#   for post in posts[:post_count]:
#     total_likes += post['like_count']
#     total_comments += post['comment_count']
    
#     total_interactions = total_likes + total_comments
#     user_info = cl.user_info_by_username(username)
#     followers_count = user_info['user']['follower_count']

#     if followers_count == 0 or post_count == 0:
#       engagement_rate = None
#     else:
#       engagement_rate = (total_interactions / post_count) / followers_count * 100
#       time.sleep(1)  
#       return engagement_rate



def extract_user_data(user: User):
    phone_numbers = extract_phone_number(user.biography)
    email = extract_email(user.biography)
    # engagement_rate = calculate_engagement_rate(user.username)

    return {
        'username': user.username,
        'full_name': user.full_name,
        'media_count': user.media_count,
        'follower_count': user.follower_count,
        'following_count': user.following_count,
        'biography': user.biography,
        # 'engagement_rate': engagement_rate,
        # 'public_email': user.public_email,
        # 'contact_phone_number': user.contact_phone_number,
        'phone_number': phone_numbers,
        'email': email,
    }


def extract_phone_number(bio):
    # phone_pattern = re.compile(r'\b(?<!\d)(?!\d{4}-\d{2}\b)\+?\d+(\s?\d+[-.\s]?\d+)?\b(?!-?\d)')
    phone_pattern = re.compile(r'\b\d+[-.\s]?\d+[-.\s]?\d+\b')
    phone_numbers = re.findall(phone_pattern, bio)
    return phone_numbers

def extract_email(bio):
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    email_matches = re.findall(email_pattern, bio)
    return email_matches

@app.route('/profile/<accountname>')
def get_profile(accountname):
    max_retries = 3
    retry_delay = 5

    for retry_number in range(1, max_retries + 1):
        try:
            profile_info = cl.user_info_by_username(accountname)
            if profile_info is not None:
                data = extract_user_data(profile_info)
                
                # Extract phone number and email from biography
                phone_numbers = extract_phone_number(data['biography'])
                email = extract_email(data['biography'])

                # Add phone number and email to the response data
                data['phone_number'] = phone_numbers
                data['email'] = email

                response = {
                    'success': True,
                    'message': 'Data retrieved successfully',
                    'data': data
                }
                json_data = json.dumps(response, ensure_ascii=False)
                return Response(json_data, content_type='application/json; charset=utf-8')
            else:
                response = {
                    'success': False,
                    'message': 'Profile not found',
                    'data': None
                }
                return jsonify(response)
        except Exception as e:
            if "429" in str(e):
                print(f"Rate limit exceeded. Retrying in {retry_delay} seconds (Retry {retry_number}/{max_retries}).")
                time.sleep(retry_delay)
            else:
                response = {
                    'success': False,
                    'message': f"An error occurred while fetching profile: {e}",
                    'data': None
                }
                return jsonify(response)

    response = {
        'success': False,
        'message': 'Max retries reached. Unable to fetch profile.',
        'data': None
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=False)