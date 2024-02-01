import os
import json
import random
from flask import Flask, render_template, session, request, redirect, url_for, jsonify, flash
from newsapi import NewsApiClient
from requests import HTTPError
from sentiment import find_sentiment
from fake_news_detector.fake_news_detector import Model
from flask_mailman import Mail, EmailMessage
from utilities import db_user_identifier, user_dict, toDateTime
import pyrebase
from dotenv import load_dotenv
from datetime import datetime
from flask_apscheduler import APScheduler

API_KEY = "7286ead268a647f4b0bb296b4f1e0c5a"

news_api = NewsApiClient(api_key=API_KEY)

config = {
  "apiKey": "AIzaSyCPKnalll7RqtoEu4gNWqD3m8WpgozUNHs",
  "authDomain": "e-voting-559ca.firebaseapp.com",
  "databaseURL": "https://e-voting-559ca-default-rtdb.firebaseio.com",
  "projectId": "e-voting-559ca",
  "storageBucket": "e-voting-559ca.appspot.com",
  "messagingSenderId": "1093868121149",
  "appId": "1:1093868121149:web:10a21eb0214e9964ee0e54",
  "measurementId": "G-LBTBH1Z3CQ"
}

app = Flask(__name__)
scheduler = APScheduler(app=app)
load_dotenv()
app.config["DEBUG"] = os.environ.get("FLASK_DEBUG")
app.config["MAIL_SERVER"] = "smtp.fastmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "knight550@fastmail.com"
app.config["MAIL_PASSWORD"] = "9tvv5el4cyq3a57d"
app.config["MAIL_DEFAULT_SENDER"] = ("YourNews", "knight550@fastmail.com")
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.secret_key = "Something weird"
mail = Mail()
mail.init_app(app)
firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()
fake_news_model = Model()
app.jinja_env.globals.update(fake_news_model=fake_news_model.predict_news, find_sentiment=find_sentiment)


sources_list = news_api.get_sources()
sources = {}
for i in sources_list["sources"]:
    sources[i["name"]] = i["category"]


def get_category(article_source):
    try:
        return sources[article_source]
    except KeyError:
        return "general"


def check_article_save(article):
    print(db.child("users").child(session["user_identifier"]).child("saved").child(article["publishedAt"]).get().val())
    saved_article = db.child("users").child(session["user_identifier"]).child("saved").child(article["publishedAt"]).get().val()
    if saved_article is None: return False
    return True


news_articles = []
preferences = []
saved = ""
email = ""
categories = ["business", "entertainment", "general", "health", "science", "technology", "sports"]
category_list = []
search_list = []

articles_fetched = False
def get_articles():
    for category in categories:
        articles = []
        category_articles = news_api.get_top_headlines(category=category, language="en", page_size=100)["articles"]
        for article in category_articles:
            article["category"] = category.title()
            article["authentication"] = fake_news_model.predict_news(article["url"])
            article["subjectivity"] = find_sentiment(article["url"], "subjectivity")
            article["author"] = "N/A" if article["author"] is None else article["author"]
            article["urlToImage"] = "/static/images/no_image_available.jpg" if (
                    article["urlToImage"] is None) else article["urlToImage"]
            articles.append(article)
        db.child("articles").child(category).set(articles)
    db.child("articles").update({"Time Fetched": datetime.utcnow().strftime('%a, %B %d, %Y | %H:%M')})
        
    print(f"Articles Fetched at {datetime.utcnow().strftime('%a, %B %d, %Y | %H:%M')}")
    articles_fetched = True        

# get_articles()
@app.route("/")
def temp():
    if "user" in session:
        return redirect("/1")
    return redirect(url_for("login"))


@app.route("/<int:page_number>", methods=["GET", "POST"])
def home(page_number):
    global news_articles, preferences, email, saved
    if "user" in session:
        email = session["user"]
        user_identifier = session["user_identifier"]
        user = db.child("users").child(user_identifier).get().val()
        if request.method == "POST":
            search_entry = request.form.get("search")
            return redirect(f"/search/{search_entry}/1")
        else:
            preferences = user["preferences"]
            if page_number == 1:
                articles = []
                for preference in preferences:
                    print(preference)
                    user_preference_articles = db.child("articles").child(preference).get().val()[:20]
                    articles += user_preference_articles
                random.shuffle(articles)
                articles_info = {"articles": articles, "article_count": len(articles), "articles_from": "feed"}
                articles_info["number_of_pages"] = int(articles_info["article_count"] / 12) + 1
                session["articles_info"] = articles_info
                db.child("users").child(user_identifier).update(articles_info)
                random.shuffle(articles)
            elif page_number == user["number_of_pages"]:
                start_index = (page_number - 1) * 12
                articles = user["articles"][start_index:]
                print("DEBUGGING!!!!!!!!")
                print(articles)
                print(start_index)
            else:
                start_index = (page_number * 12) - 12
                end_index = page_number * 12
                articles = user["articles"][start_index:end_index]
            top_category1 = random.choice(preferences)
            preferences.remove(top_category1)
            top_category2 = random.choice(preferences)
            preferences.append(top_category1)
            top_articles1 = news_api.get_top_headlines(category=top_category1, language="en", page=3)["articles"]
            top_articles2 = news_api.get_top_headlines(category=top_category2, language="en", page=3)["articles"]
            if page_number == 1:
                articles = articles[:12]
            return render_template("index.html", page_number=page_number, articles=articles,
                                   toDateTime=toDateTime, top_category1=top_category1, top_category2=top_category2,
                                   top_articles1=top_articles1, top_articles2=top_articles2,
                                   check_article_save=check_article_save, json=json, user=user)
    else:
        return redirect(url_for("login"))


@app.route("/account", methods=["GET", "POST"])
def account():
    if "user" in session:
        user_id = session["user_identifier"]
        user = db.child("users").child(user_id).get().val()
        if request.method == "POST":
            search_entry = request.form.get("search")
            if search_entry is not None:
                return redirect(f"/search/{search_entry}/1")
            else:
                first_name = request.form.get("first_name")
                last_name = request.form.get("last_name")
                preferences = request.form.getlist("preferences")
                user_update_dict = user_dict(first_name, last_name, session["user"], preferences, user_id)
                db.child("users").child(user_id).update(user_update_dict)
                session["user"] = request.form.get("email")
                flash("Account information updated sucessfully!")
                return render_template("account.html", user=user, username=email,
                                       success="Account details updated successfully!")
        else:
            return render_template("account.html", user=user)
    else:
        return redirect("/login")


@app.route("/search/<search_variable>/<int:page_number>", methods=["GET", "POST"])
def search(search_variable, page_number):
    global search_list
    if "user" in session:
        user_identifier = session["user_identifier"]
        user = db.child("users").child(user_identifier).get().val()
        if request.method == "POST":
            search_variable = request.form.get("search")
            search_list = news_api.get_everything(
                q=f"{search_variable}", language="en", page_size=100)["articles"]
        if page_number == 1:
            search_list = news_api.get_everything(
                q=f"{search_variable}", page_size=100)["articles"]
            search_info = {"search_list": search_list, "search_list_count": len(search_list)}
            search_info["search_list_number_of_pages"] = int(search_info["search_list_count"] / 12) + 1
            db.child("users").child(user_identifier).update(search_info)
        elif page_number == user["search_list_number_of_pages"]:
            start_index = (page_number - 1) * 12
            search_list = user["search_list"][start_index:]
        else:
            start_index = (page_number * 12) - 12
            end_index = page_number * 12
            search_list = user["search_list"][start_index:end_index]
        if page_number == 1:
                search_list = search_list[:12]
        return render_template("search_results.html", page_number=page_number, search_list=search_list, search=search_variable,
                                username=user_identifier, toDateTime=toDateTime, get_category=get_category, user=user,
                                find_sentiment=find_sentiment, check_article_save=check_article_save, json=json)
            
    else:
        return redirect("/login")



@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        email = request.form.get('email')
        generated_user_id = db_user_identifier(email)
        mail_check = db.child("users").child(generated_user_id).get().val()
        if mail_check is None:
            flash("Email not associated with an account", "error")
            return render_template("change_password.html", error="Email not associated with an account")
        auth.send_password_reset_email(email)
        flash("A password reset email has been sent to the email provided", "success")
        return redirect("/change_password")
    else:
        return render_template("change_password.html")

@app.route("/saved_articles", methods=["GET", "POST"])
def saved_articles():
    if "user" in session:
        if request.method == "POST":
            search_entry = request.form.get("search")
            return redirect(f"/search/{search_entry}/1")
        else:
            email = session["user"]
            is_empty = False
            load_saves = db.child("users").child(db_user_identifier(email)).child("saved").get().each()
            if load_saves is None or len(load_saves) == 0:
                is_empty = True
                return render_template("saves.html", username=email, is_empty=is_empty)
            if type(load_saves) is not list:
                load_saves = load_saves.split("*delimiter*")
            saved_list = []
            for article in load_saves:
                saved_list.append(article.val())
            return render_template("saves.html", username=email, saved_list=saved_list, is_empty=is_empty,
                                   toDateTime=toDateTime, get_category=get_category, find_sentiment=find_sentiment,
                                   json=json)
    else:
        return redirect("/login")


@app.route("/save", methods=["POST"])
def save():
    if "user" in session:
        user_identifier = session["user_identifier"]
        article = json.loads(request.form.get("article"))
        link = request.form.get("link")
        try:
            temp = article["category"]
        except:
            temp = link.split("/")
            print("SAVE DEBUGGING STARTS HERE !!!")
            print(temp)
            if temp[1] == "category":
                article["category"] = temp[2]
            else:
                article["category"] = get_category(article["source"]["name"])
                article["authentication"] = fake_news_model.predict_news(article["url"])
                article["subjectivity"] = find_sentiment(article["url"], "subjectivity")
        saved_dict = db.child("users").child(user_identifier).child("saved").get().val()
        try:
            saved_dict[article["publishedAt"]] = article
            db.child("users").child(user_identifier).update({"saved": saved_dict})
        except TypeError:
            saved_dict = {article["publishedAt"]: article}
            db.child("users").child(user_identifier).child("saved").set(saved_dict)
        
        return redirect(link)
    else:
        return redirect("/login")


@app.route("/delete_save", methods=["POST"])
def delete_save():
    user_identifier = session["user_identifier"]
    article = json.loads(request.form.get("article"))
    link = request.form.get("link")
    db.child("users").child(user_identifier).child("saved").child(article["publishedAt"]).remove()
    return redirect(link)


@app.route("/analyzer", methods=["GET"])
def analyzer():
    if "user" in session:
        analyze = False
        return render_template("news_analyzer.html", username=email, analyze=analyze)
    else:
        return redirect("/login")


@app.route("/analyzer_process", methods=["POST"])
def process():
    news = request.form.get("news")
    sentiment_subjectivity = find_sentiment(news, "subjectivity", content=True)
    sentiment_polarity = find_sentiment(news, "polarity", content=True)
    fake_news_detect = fake_news_model.predict_news(news, content=True)
    return jsonify({
        "bias": f"This article seems {sentiment_subjectivity}",
        "polarity": f"It reads as {sentiment_polarity}",
        "fake_news_detect": fake_news_detect,
    })


@app.route("/category/<category_variable>/<int:page_number>", methods=["GET", "POST"])
def category(category_variable, page_number):
    if "user" in session:
        if request.method == "POST":
            search_entry = request.form.get("search")
            return redirect(f"/search/{search_entry}/1")
        else:
            user_identifier = session["user_identifier"]
            user = db.child("users").child(user_identifier).get().val()
            if page_number == 1:
                category_list = db.child("articles").child(category_variable).get().val()
                category_info = {"category_list": category_list, "category_list_count": len(category_list)}
                category_info["category_list_number_of_pages"] = int(category_info["category_list_count"] / 12) + 1
                db.child("users").child(user_identifier).update(category_info)
            elif page_number == user["category_list_number_of_pages"]:
                start_index = (page_number - 1) * 12
                category_list = user["category_list"][start_index:]
            else:
                start_index = (page_number * 12) - 12
                end_index = page_number * 12
                category_list = user["category_list"][start_index:end_index]
            if page_number == 1:
                    category_list = category_list[:12]
            
            return render_template("category.html", category_list=category_list, category=category_variable,
                                   user=user, toDateTime=toDateTime, len=len, check_article_save=check_article_save, 
                                   json=json, page_number=page_number)
    else:
        return redirect("/login")



@app.route("/contact", methods=["GET", "POST"])
def contact():
    if "user" in session:
        username_contact = session["user"]
        if request.method == "POST":
            search_entry = request.form.get("search")
            if search_entry is not None:
                return redirect(f"/search/{search_entry}/1")
            else:
                name = request.form.get("name")
                email = request.form.get("email")
                number = request.form.get("number")
                subject = request.form.get("subject")
                message = request.form.get("message")
                e_msg = EmailMessage(
                    f"User {session['user_identifier']} sent a message",
                    f"""
                     Name: {name}
                     Email: {email}
                     Number: {number}
                     Subject: {subject}
                     Message: {message}
                    """,
                    "knight550@fastmail.com",
                    ["knight550@fastmail.com"]
                )
                e_msg.send()
                return render_template("contact.html", username=username_contact, success="Your message has been sent.")
        else:
            return render_template("contact.html", username=username_contact)
    else:
        return redirect("/login")


@app.route("/delete")
def delete():
    db.child("users").child(session["user_identifier"]).remove()
    flash("Account Successfully Deleted", "success")
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password_login")
        try:
            auth.sign_in_with_email_and_password(email, password)
        except HTTPError:
            flash("Invalid email or password", "error")
            return redirect(url_for("login"))
        session["user"] = email
        session["user_identifier"] = db_user_identifier(email)
        return redirect("/")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        preferences_register = request.form.getlist("preferences")
        print(preferences_register)
        try:
            auth.create_user_with_email_and_password(email, password)
        except HTTPError:
            flash("Email has already been taken", "error")
            return redirect(url_for("register"))
        user_id = db_user_identifier(email)
        new_user = user_dict(first_name, last_name, email, preferences_register, user_id)
        db.child("users").child(user_id).set(new_user)
        flash("Account Created Successfully!", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/article_request_scheduler")
def article_request_scheduler(request):
    if articles_fetched:
        pass
    else:
        get_articles()
    articles_fetched = False
    return "Article Request Scheduler Successful"


@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("articles", None)
    session.pop("number_of_pages", None)
    session.pop("article_count", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    scheduler.add_job(id="Article_Request", func=get_articles, trigger="cron", day_of_week="mon-sun", hour=3, minute=30)
    scheduler.start()
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080
    app.run(port=PORT,host='0.0.0.0',debug=True)
