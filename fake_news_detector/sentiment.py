from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from utilities import get_content

analyzer = SentimentIntensityAnalyzer()

def find_sentiment(article_url, sentiment_type, content=False):
    if content:
        article = article_url
    else:
        article = get_content(article_url)
    if article is None:
        return "N/A"

    sentiment = analyzer.polarity_scores(article)
    polarity = sentiment['compound']
    subjectivity = abs(sentiment['pos'] - sentiment['neg'])  # crude approximation

    if sentiment_type == "polarity":
        if polarity >= 0.75:
            return "Extremely Positive"
        elif polarity >= 0.5:
            return "Significantly Positive"
        elif polarity >= 0.3:
            return "Fairly Positive"
        elif polarity >= 0.1:
            return "Slightly Positive"
        elif polarity <= -0.1:
            return "Slightly Negative"
        elif polarity <= -0.3:
            return "Fairly Negative"
        elif polarity <= -0.5:
            return "Significantly Negative"
        elif polarity <= -0.75:
            return "Extremely Negative"
        else:
            return "Neutral"
    
    elif sentiment_type == "subjectivity":
        if subjectivity >= 0.75:
            return "Extremely Subjective"
        elif subjectivity >= 0.5:
            return "Fairly Subjective"
        elif subjectivity >= 0.3:
            return "Fairly Objective"
        elif subjectivity >= 0.1:
            return "Extremely Objective"
        else:
            return "Neutral"
    
    else:
        raise ValueError(f"Invalid sentiment_type '{sentiment_type}'. Use 'polarity' or 'subjectivity'")
