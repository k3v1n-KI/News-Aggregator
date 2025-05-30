from textblob import TextBlob
from utilities import get_content


def find_sentiment(article_url, sentiment_type, content=False):
    if content:
        article = article_url
    else:
        article = get_content(article_url)
    if article is None:
        return "N/A"
    news = TextBlob(article)
    polarity_list = []
    subjectivity_list = []
    for sentence in news.sentences:
        print(sentence.sentiment[0])
        polarity_list.append(sentence.sentiment[0])
        subjectivity_list.append(sentence.sentiment[1])
    print(polarity_list)
    print(len(polarity_list))
    try:
        polarity_avg = sum(polarity_list) / len(polarity_list)
        subjectivity_avg = sum(subjectivity_list) / len(subjectivity_list)
    except ZeroDivisionError:
        return "N/A"
    result = "N/A"
    if sentiment_type == "polarity":
        if polarity_avg >= 0.75:
            result = "Extremely Positive"
        elif polarity_avg >= 0.5:
            result = "Significantly Positive"
        elif polarity_avg >= 0.3:
            result = "Fairly Positive"
        elif polarity_avg >= 0.1:
            result = "Slightly Positive"
        elif polarity_avg <= -0.1:
            result = "Slightly Negative"
        elif polarity_avg <= -0.3:
            result = "Fairly Negative"
        elif polarity_avg <= -0.5:
            result = "Significantly Negative"
        elif polarity_avg <= -0.75:
            result = "Extremely Negative"
        else:
            result = "Neutral"
        return result
    elif sentiment_type == "subjectivity":
        if subjectivity_avg >= 0.75:
            result = "Extremely Subjective"
        elif subjectivity_avg >= 0.5:
            result = "Fairly Subjective"
        elif subjectivity_avg >= 0.3:
            result = "Fairly Objective"
        elif subjectivity_avg >= 0.1:
            result = "Extremely Objective"
        return result
    
    else:
        raise ValueError(f"find_sentiment() has no value '{sentiment_type}'. Either 'polarity' or 'subjectivity'")
