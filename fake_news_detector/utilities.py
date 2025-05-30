from newspaper import Article, ArticleException
from datetime import datetime

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


def get_content(url):
    try:
        article = Article(url.strip())
        article.download()
        article.parse()
        article.nlp()
        if article.text == "" or article.text is None or len(article.text) == 0:
            return None
        return article.text
    except ArticleException:
        return None


def toDateTime(date_string):
    date_processing = date_string.replace(
        'T', '-').replace(':', '-').replace("Z", "").replace(" ", "-").split('-')
    date_processing = [int(v) for v in date_processing]
    date_out = datetime(*date_processing)
    return date_out
