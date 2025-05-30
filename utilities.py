import trafilatura
from datetime import datetime
import time

def db_user_identifier(email: str):
    index = email.index("@")
    formatted_username = email[:index].replace(".", "")
    return formatted_username


def user_dict(first_name, last_name, email, preferences, user_id):
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "preferences": preferences,
        "saved_article": None,
        "user_id": user_id
    }


def get_content(url, retries=3, delay=2):
    for i in range(retries):
        try:
            downloaded = trafilatura.fetch_url(url, timeout=10)
            if downloaded:
                return trafilatura.extract(downloaded)
        except Exception as e:
            print(f"[Retry {i+1}] Failed to fetch {url}: {e}")
            time.sleep(delay)
    return None


def toDateTime(date_string):
    date_processing = date_string.replace(
        'T', '-').replace(':', '-').replace("Z", "").replace(" ", "-").split('-')
    date_processing = [int(v) for v in date_processing]
    date_out = datetime(*date_processing)
    return date_out
