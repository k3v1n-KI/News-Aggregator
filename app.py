import json
import random
from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from newsapi import NewsApiClient
from sentiment import find_sentiment
from fake_news_detector.fake_news_detector import Model
from newspaper import Article
from flask_mail import Mail, Message

API_KEY = "7286ead268a647f4b0bb296b4f1e0c5a"

news_api = NewsApiClient(api_key=API_KEY)

app = Flask(__name__)   
app.secret_key = "Something weird"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "knightp550@gmail.com"
app.config["MAIL_PASSWORD"] = "the_dark_knight"
app.config["MAIL_DEFAULT_SENDER"] = ("YourNews", "knightp550@gmail.com")
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
mail = Mail(app)
db = SQLAlchemy(app)
fake_news_model = Model()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    preferences = db.Column(db.Text, nullable=False)
    saved = db.Column(db.Text, nullable=True)

    def __repr__(self) -> str:
        return "User" + str(self.id)


sources_list = news_api.get_sources()
sources = {}
for i in sources_list["sources"]:
    sources[i["name"]] = i["category"]


def get_content(url):
    try:
        article = Article(url.strip())
        article.download()
        article.parse()
        article.nlp()
        if article.text == "" or article.text is None or len(article.text) == 0:
            return None
        return article.text
    except:
        return None


def toDateTime(date_string):
    date_processing = date_string.replace(
        'T', '-').replace(':', '-').replace("Z", "").replace(" ", "-").split('-')
    date_processing = [int(v) for v in date_processing]
    date_out = datetime(*date_processing)
    return date_out


def get_category(article_source):
    try:
        return sources[article_source]
    except KeyError:
        return "general"


def check_article_save(article):
    saves = Users.query.filter_by(username=username).all()[0].saved
    if saves is None:
        return False
    saves = saves.split("*delimiter*")
    if json.dumps(article) in saves:
        return True
    return False


news_articles = []
preferences = []
saved = ""
username = ""
categories = ["business, entertainment",
              "general", "health", "science", "technology"]
category_list = []
search_list = []


@app.route("/", methods=["GET", "POST"])
def home():
    global news_articles, preferences, username, saved
    if "user" in session:
        username = session["user"]
        if request.method == "POST":
            search_entry = request.form.get("search")
            return redirect(f"/search/{search_entry}")
        else:
            preferences = Users.query.filter_by(
                username=username).all()[0].preferences
            preferences = preferences.split()
            saved = Users.query.filter_by(
                username=username).all()[0].saved
            if saved is None:
                saved = ""
            saved = saved.split(";")
            for preference in preferences:
                preference_list = news_api.get_top_headlines(
                    category=f'{preference}', language="en")["articles"]
                for article in preference_list:
                    article_string = json.dumps(article)
                    if article_string in saved:
                        article["saved"] = True
                    else:
                        article["saved"] = False
                    article["category"] = preference.title()
                    if article["author"] is None:
                        article["author"] = "N/A"
                    scraped_content = get_content(article["url"])
                    if scraped_content is not None:
                        article["content"] = scraped_content
                        print("Scrapped")
                    else:
                        if article["content"] is not None and article["description"] is not None and article["title"] \
                                is not None:
                            article["content"] = article["title"] + article["description"] + article["content"]
                            print("Not scraped")
                        elif article["content"] is None and article["description"] is not None and article["title"] \
                                is not None:
                            article["content"] = None
                            print("No content")
                    if article["urlToImage"] is None:
                        article["urlToImage"] = url_for("static", filename="images/no_image_available.jpg")
                news_articles += preference_list
            random.shuffle(news_articles)
            top_category1 = random.choice(preferences)
            top_category2 = random.choice(preferences)
            while top_category1 == top_category2:
                top_category2 = random.choice(preferences)
            top_articles1 = []
            top_articles2 = []
            for article in news_articles:
                if article["category"] == top_category1.title():
                    top_articles1.append(article)
                elif article["category"] == top_category2.title():
                    top_articles2.append(article)
            return render_template("index.html", username=username, news_articles=news_articles,
                                   toDateTime=toDateTime, top_articles1=top_articles1, top_articles2=top_articles2,
                                   find_sentiment=find_sentiment, fake_news_model=fake_news_model.predict_news,
                                   check_article_save=check_article_save, json=json)
    else:
        return redirect("/login")


@app.route("/2", methods=["GET", "POST"])
def home2():
    global news_articles, preferences, username
    if "user" in session:
        if request.method == "POST":
            search_entry = request.form.get("search")
            return redirect(f"/search/{search_entry}")
        else:
            top_category1 = random.choice(preferences)
            top_category2 = random.choice(preferences)
            while top_category1 == top_category2:
                top_category2 = random.choice(preferences)
            top_articles1 = []
            top_articles2 = []
            for article in news_articles:
                if article["category"] == top_category1.title():
                    top_articles1.append(article)
                elif article["category"] == top_category2.title():
                    top_articles2.append(article)
            return render_template("index2.html", username=username, news_articles=news_articles, toDateTime=toDateTime,
                                   top_articles1=top_articles1, top_articles2=top_articles2,
                                   find_sentiment=find_sentiment, fake_news_model=fake_news_model.predict_news,
                                   check_article_save=check_article_save, json=json)
    else:
        return redirect("/login")


@app.route("/3", methods=["GET", "POST"])
def home3():
    global news_articles, preferences, username
    if "user" in session:
        if request.method == "POST":
            search_entry = request.form.get("search")
            return redirect(f"/search/{search_entry}")
        else:
            # username = session["user"]
            top_category1 = random.choice(preferences)
            top_category2 = random.choice(preferences)
            while top_category1 == top_category2:
                top_category2 = random.choice(preferences)
            top_articles1 = []
            top_articles2 = []
            for article in news_articles:
                if article["category"] == top_category1.title():
                    top_articles1.append(article)
                elif article["category"] == top_category2.title():
                    top_articles2.append(article)
            return render_template("index3.html", username=username, news_articles=news_articles, toDateTime=toDateTime,
                                   top_articles1=top_articles1, top_articles2=top_articles2,
                                   find_sentiment=find_sentiment, fake_news_model=fake_news_model.predict_news,
                                   check_article_save=check_article_save, json=json)
    else:
        return redirect("/login")


@app.route("/account", methods=["GET", "POST"])
def account():
    if "user" in session:
        user = Users.query.filter_by(username=username).all()[0]
        if request.method == "POST":
            search_entry = request.form.get("search")
            if search_entry is not None:
                return redirect(f"/search/{search_entry}")
            else:
                user.first_name = request.form.get("first_name")
                user.last_name = request.form.get("last_name")
                user.email = request.form.get("email")
                user.username = request.form.get("username")
                user.preferences = " ".join(
                    request.form.getlist("preferences"))
                db.session.commit()
                session["user"] = request.form.get("username")
                return render_template("account.html", user=user, username=username,
                                       success="Account details updated successfully!")
        else:
            return render_template("account.html", user=user)
    else:
        return redirect("/login")


@app.route("/search/<search_variable>", methods=["GET", "POST"])
def search(search_variable):
    global search_list
    if "user" in session:
        if request.method == "POST":
            search_variable = request.form.get("search")
        search_list = news_api.get_everything(
            q=f"{search_variable}", page_size=100)["articles"]
        return render_template("search_results.html", search_list=search_list[0:20], search=search_variable,
                               username=username, toDateTime=toDateTime, get_category=get_category,
                               find_sentiment=find_sentiment, check_article_save=check_article_save, json=json)
    else:
        return redirect("/login")


@app.route("/search/<search_variable>/2", methods=["GET", "POST"])
def search2(search_variable):
    global search_list
    if "user" in session:
        if request.method == "POST":
            search_variable = request.form.get("search")
            return redirect(f"/search/{search_variable}")
        return render_template("search2_results.html", search_list=search_list[20:40], search=search_variable,
                               username=username, toDateTime=toDateTime, get_category=get_category,
                               find_sentiment=find_sentiment, check_article_save=check_article_save, json=json)
    else:
        return redirect("/login")


@app.route("/search/<search_variable>/3", methods=["GET", "POST"])
def search3(search_variable):
    global search_list
    if "user" in session:
        if request.method == "POST":
            search_variable = request.form.get("search")
            return redirect(f"/search/{search_variable}")
        return render_template("search3_results.html", search_list=search_list[40:60], search=search_variable,
                               username=username, toDateTime=toDateTime, get_category=get_category,
                               find_sentiment=find_sentiment, check_article_save=check_article_save, json=json)
    else:
        return redirect("/login")


@app.route("/search/<search_variable>/4", methods=["GET", "POST"])
def search4(search_variable):
    global search_list
    if "user" in session:
        if request.method == "POST":
            search_variable = request.form.get("search")
            return redirect(f"/search/{search_variable}")
        return render_template("search4_results.html", search_list=search_list[60:80], search=search_variable,
                               username=username, toDateTime=toDateTime, get_category=get_category,
                               find_sentiment=find_sentiment, check_article_save=check_article_save, json=json)
    else:
        return redirect("/login")


@app.route("/search/<search_variable>/5", methods=["GET", "POST"])
def search5(search_variable):
    global search_list
    if "user" in session:
        if request.method == "POST":
            search_variable = request.form.get("search")
            return redirect(f"/search/{search_variable}")
        return render_template("search5_results.html", search_list=search_list[80:100], search=search_variable,
                               username=username, toDateTime=toDateTime, get_category=get_category,
                               find_sentiment=find_sentiment, check_article_save=check_article_save, json=json)
    else:
        return redirect("/login")


@app.route("/email_check", methods=["GET", "POST"])
def email_check():
    if request.method == "POST":
        email = request.form.get('email')
        email_list = Users.query.filter_by(email=email).all()
        if len(email_list) == 0:
            return render_template("email_check.html", error="Email not associated with an account")
        else:
            session["email"] = email
            return redirect("/change_password")
    else:
        return render_template("email_check.html")


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        email = session["email"]
        password = request.form.get("password")
        user = Users.query.filter_by(email=email).all()[0]
        user.password = password
        db.session.commit()
        return redirect(url_for("login", success="Password changed successfully"))
    else:
        return render_template("change_password.html")


@app.route("/change_password_user", methods=["GET", "POST"])
def change_password_user():
    if request.method == "POST":
        old_password = request.form.get("old_password")
        password = request.form.get("password")
        user = Users.query.filter_by(username=username).all()[0]
        if user.password != old_password:
            return render_template("change_password_user.html", error="Old password is invalid")
        user.password = password
        db.session.commit()
        return redirect(url_for("account", success="Password changed successfully"))
    else:
        return render_template("change_password_user.html")


@app.route("/saved_articles", methods=["GET", "POST"])
def saved_articles():
    if "user" in session:
        if request.method == "POST":
            search_entry = request.form.get("search")
            return redirect(f"/search/{search_entry}")
        else:
            global username
            username = session["user"]
            is_empty = False
            load_saves = Users.query.filter_by(
                username=username).all()[0].saved
            if load_saves == "" or len(load_saves) == 0:
                is_empty = True
                return render_template("saves.html", username=username, is_empty=is_empty)
            if type(load_saves) is not list:
                load_saves = load_saves.split("*delimiter*")
            saved_list = []
            for article in load_saves:
                saved_list.append(json.loads(article))
            return render_template("saves.html", username=username, saved_list=saved_list, is_empty=is_empty,
                                   toDateTime=toDateTime, get_category=get_category, find_sentiment=find_sentiment,
                                   json=json)
    else:
        return redirect("/login")


@app.route("/save", methods=["POST"])
def save():
    if "user" in session:
        saved_articles_toSave = Users.query.filter_by(
            username=username).all()[0]
        article = request.form.get("article")
        link = request.form.get("link")
        if saved_articles_toSave.saved is None:
            saved_articles_toSave.saved = ""
        if len(saved_articles_toSave.saved) == 0:
            saved_articles_toSave.saved = article
        else:
            saved_articles_toSave.saved += ("*delimiter*" + article)
        db.session.commit()
        return redirect(link)
    else:
        return redirect("/login")


@app.route("/delete_save", methods=["POST"])
def delete_save():
    saved_articles_delete = Users.query.filter_by(
        username=username).all()[0]
    article = request.form.get("article")
    link = request.form.get("link")
    saved_list = saved_articles_delete.saved.split("*delimiter*")
    saved_list.remove(article)
    saved_articles_delete.saved = "*delimiter*".join(saved_list)
    db.session.commit()
    return redirect(link)


@app.route("/analyzer", methods=["GET"])
def analyzer():
    if "user" in session:
        analyze = False
        return render_template("news_analyzer.html", username=username, analyze=analyze)
    else:
        return redirect("/login")


@app.route("/analyzer_process", methods=["POST"])
def process():
    news = request.form.get("news")
    sentiment_subjectivity = find_sentiment(news, "subjectivity")
    sentiment_polarity = find_sentiment(news, "polarity")
    fake_news_detect = fake_news_model.predict_news(news)
    return jsonify({
        "bias": f"This article seems {sentiment_subjectivity}",
        "polarity": f"It reads as {sentiment_polarity}",
        "fake_news_detect": fake_news_detect,
    })


@app.route("/category/<category_variable>", methods=["GET", "POST"])
def category(category_variable):
    global category_list
    if "user" in session:
        if request.method == "POST":
            search_entry = request.form.get("search")
            return redirect(f"/search/{search_entry}")
        else:
            category_list = news_api.get_top_headlines(
                category=f'{category_variable.lower()}', language="en", page_size=100)["articles"]
            return render_template("category.html", category_list=category_list[0:20], category=category_variable,
                                   username=username, toDateTime=toDateTime, len=len, find_sentiment=find_sentiment,
                                   check_article_save=check_article_save, json=json)
    else:
        return redirect("/login")


@app.route("/category/<category_variable>/2", methods=["GET", "POST"])
def category2(category_variable):
    if "user" in session:
        if request.method == "POST":
            search_entry = request.form.get("search")
            return redirect(f"/search/{search_entry}")
        else:
            return render_template("category2.html", category_list=category_list[20:40], category=category_variable,
                                   username=username, toDateTime=toDateTime, len=len, find_sentiment=find_sentiment,
                                   check_article_save=check_article_save, json=json)
    else:
        return redirect("/login")


@app.route("/category/<category_variable>/3", methods=["GET", "POST"])
def category3(category_variable):
    if "user" in session:
        if request.method == "POST":
            search_entry = request.form.get("search")
            return redirect(f"/search/{search_entry}")
        else:
            return render_template("category3.html", category_list=category_list[40:60], category=category_variable,
                                   username=username, toDateTime=toDateTime, len=len, find_sentiment=find_sentiment,
                                   check_article_save=check_article_save, json=json)
    else:
        return redirect("/login")


@app.route("/category/<category_variable>/4", methods=["GET", "POST"])
def category4(category_variable):
    if "user" in session:
        if request.method == "POST":
            search_entry = request.form.get("search")
            return redirect(f"/search/{search_entry}")
        else:
            return render_template("category4.html", category_list=category_list[60:80], category=category_variable,
                                   username=username, toDateTime=toDateTime, len=len, find_sentiment=find_sentiment,
                                   check_article_save=check_article_save, json=json)
    else:
        return redirect("/login")


@app.route("/category/<category_variable>/5", methods=["GET", "POST"])
def category5(category_variable):
    if "user" in session:
        if request.method == "POST":
            search_entry = request.form.get("search")
            return redirect(f"/search/{search_entry}")
        else:
            return render_template("category5.html", category_list=category_list[80:100], category=category_variable,
                                   username=username, toDateTime=toDateTime, len=len, find_sentiment=find_sentiment,
                                   check_article_save=check_article_save, json=json)
    else:
        return redirect("/login")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if "user" in session:
        username_contact = session["user"]
        if request.method == "POST":
            search_entry = request.form.get("search")
            if search_entry is not None:
                return redirect(f"/search/{search_entry}")
            else:
                name = request.form.get("name")
                email = request.form.get("email")
                number = request.form.get("number")
                subject = request.form.get("subject")
                message = request.form.get("message")
                msg = Message(subject, sender=(name, "knightp550@gmail.com"), recipients=["knightp550@gmail.com"])
                msg.body = message + f"""
                Name: {name}
                Email: {email}
                Phone Number: {number}
                """
                mail.send(msg)
                return render_template("contact.html", username=username_contact, success="Your message has been sent.")
        else:
            return render_template("contact.html", username=username_contact)
    else:
        return redirect("/login")


@app.route("/delete/<int:id>")
def delete(id_delete):
    user = Users.query.get_or_404(id_delete)
    db.session.delete(user)
    db.session.commit()
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_login = request.form.get("username_login")
        password = request.form.get("password_login")
        user_validate = Users.query.filter_by(
            username=username_login, password=password).all()
        if len(user_validate) == 0:
            return render_template("login.html", invalid="Invalid username or password")
        else:
            session["user"] = username_login
            return redirect("/")

    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        username_register = request.form.get("username")
        password = request.form.get("password")
        preferences_register = request.form.getlist("preferences")
        user = Users(first_name=first_name, last_name=last_name, email=email,
                     username=username_register, password=password, preferences=" ".join(preferences_register))
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/test")
def test():
    return render_template("tech-category-02.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True, port="4995")
