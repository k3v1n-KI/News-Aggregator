import pickle
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import re
import tensorflow as tf
from tensorflow import keras
from utilities import get_content

nlp = spacy.load("en_core_web_sm")


def preprocessor(text):
    text = text.lower()
    text = re.sub('<[^>]*>', '', text)
    emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', text)
    text = re.sub('[\W]+', ' ', text.lower()) + ''.join(emoticons).replace('-', '')
    doc = nlp(text)
    text = ' '.join([token.lemma_ for token in doc if token.text not in STOP_WORDS])
    return text


class Model:
    def __init__(self) -> None:
        self.model_file_name = "fake_news_detector/model_final"
        self.tokenizer_file_name = "fake_news_detector/tokenizer"
        another_strategy = tf.distribute.MirroredStrategy()
        with another_strategy.scope():
            load_options = tf.saved_model.LoadOptions(experimental_io_device='/job:localhost')
            self.model_tf = tf.keras.models.load_model(self.model_file_name, options=load_options)
        self.tokenizer = pickle.load(open(self.tokenizer_file_name, "rb"))

    def predict_news(self, article, content=False):
        if content:
            news = article
        else:
            news = get_content(article)
        if news is None:
            return "N/A"
        news = preprocessor(news)
        sequences = self.tokenizer.texts_to_sequences([news])
        padded_sequences = keras.preprocessing.sequence.pad_sequences(sequences, maxlen=1000)
        prediction = (self.model_tf.predict(padded_sequences) >= 0.5).astype(int)[0][0]
        if prediction == 1:
            return "Verified Credibility"
        else:
            return "Unverified Credibility."
