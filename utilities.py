import trafilatura
import time
from datetime import datetime
import requests

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


def get_content(url, max_retries=3, timeout=5):
    headers = {"User-Agent": "Mozilla/5.0"}
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                print(f"[Attempt {attempt + 1}] Non-200 response: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[Attempt {attempt + 1}] Error fetching URL: {e}")
        if attempt == 2:
            print("Max retries reached. Moving on")
        time.sleep(0.5)
    return None


def toDateTime(date_string):
    date_processing = date_string.replace(
        'T', '-').replace(':', '-').replace("Z", "").replace(" ", "-").split('-')
    date_processing = [int(v) for v in date_processing]
    date_out = datetime(*date_processing)
    return date_out
