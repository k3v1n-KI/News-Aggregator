# 📰 News Aggregator App

This is a Flask-based news aggregator that allows users to browse categorized articles, perform sentiment analysis, detect fake news using an AI model, and manage their preferences and saved articles.

---

## 🚀 Features

- 🔐 User Authentication (via Firebase)
- 🗞️ News Feed tailored to user preferences
- 🔎 Search articles by keyword
- 🧠 Sentiment Analysis & Fake News Detection (via PyTorch model)
- 💌 Contact Form with email integration
- 💾 Firebase Realtime Database for user/session data
- 🌐 Deployed using Docker on Google Cloud Run

---

## 🧱 Tech Stack

- **Backend**: Flask
- **Frontend**: Jinja2 templates + CSS/JS
- **Database**: Firebase Realtime DB
- **AI**: PyTorch (RNN fake news classifier)
- **Hosting**: Google Cloud Run + Artifact Registry
- **Build**: Docker

---

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/news-aggregator.git
cd news-aggregator
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file and add the following:

```env
FLASK_DEBUG=1
PORT=8080
NEWS_API_KEY=your_newsapi_key
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_DB_URL=https://your_project.firebaseio.com
FIREBASE_STORAGE_BUCKET=your_project.appspot.com
```

### 5. Run locally

```bash
python main.py
```

---

## 🐳 Docker Deployment (Cloud Run)

### 1. Build & Submit Docker Image to Artifact Registry

```bash
gcloud builds submit --tag northamerica-northeast2-docker.pkg.dev/e-voting-559ca/news-aggregator-repo/news-aggregator-app .
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy news-aggregator \
  --image northamerica-northeast2-docker.pkg.dev/e-voting-559ca/news-aggregator-repo/news-aggregator-app \
  --region northamerica-northeast2 \
  --allow-unauthenticated \
  --timeout=300 \
  --set-env-vars FLASK_DEBUG=1,PORT=8080,NEWS_API_KEY=your_newsapi_key,FIREBASE_API_KEY=your_firebase_api_key,FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com,FIREBASE_DB_URL=https://your_project.firebaseio.com,FIREBASE_STORAGE_BUCKET=your_project.appspot.com
```

---

## 🧠 AI Model Integration

The app uses a PyTorch-based RNN model to classify news as fake or real. The model and tokenizer should be saved under:

```
fake_news_detector/models/
├── fake_news_rnn_model.pth
├── tokenizer/
```

Ensure the path is correct when deploying.

---

## 📁 Project Structure

```
.
├── main.py
├── Dockerfile
├── requirements.txt
├── .env
├── templates/
├── static/
├── utilities.py
├── sentiment.py
├── fake_news_detector/
│   ├── fn_detector.py
│   └── models/
```

---

## 📝 License

This project is licensed under the MIT License.
