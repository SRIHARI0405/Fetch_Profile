import instaloader

L = instaloader.Instaloader()

INSTAGRAM_USERNAME = "loopstar154"
INSTAGRAM_PASSWORD = "Starbuzz6@"

# user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
# L.context._session.headers["User-Agent"] = user_agent

try:
    L.context.max_connection_attempts = 10
    L.context.request_timeout = 86400
    L.context.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    with open('loopstar154_1', 'wb') as f:
        L.context.save_session_to_file(f)
except Exception as e:
    print(f"An error occurred: {e}")
