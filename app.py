import datetime
import os
from flask import Flask, render_template, request, session, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
import gunicorn


load_dotenv()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    client = MongoClient(os.getenv("MONGODB_URI"))
    app.db = client.emotionstagebuch
    password = os.getenv("PASSWORD")

    entries = []

    @app.route("/", methods=["GET", "POST"])
    def home():
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        else:
            sorted_entries = [
                (
                    entry["content_situation"],
                    entry["content_reaktion"],
                    entry["content_verhalten"],
                    datetime.datetime.strptime(entry["date"], "%d.%m.%Y, %H:%M") + datetime.timedelta(hours=2),
                )
                for entry in app.db.emotionen.find({})
            ]
            sorted_entries = sorted(sorted_entries, key=lambda x: x[3], reverse=True)

            formatted_entries = [
                (
                    entry[0],
                    entry[1],
                    entry[2],
                    entry[3].strftime("%d. %b %Y, %H:%M"),
                )
                for entry in sorted_entries
            ]

            return render_template("home.html", entries=formatted_entries)

    @app.route("/neu/", methods=["GET", "POST"])
    def neu():
        if request.method == "POST":
            entry_situation = request.form.get("content_situation")
            entry_reaktion = request.form.get("content_reaktion")
            entry_verhalten = request.form.get("content_verhalten")
            formatted_date = datetime.datetime.now().strftime("%d.%m.%Y, %H:%M")
            app.db.emotionen.insert_one({"content_situation": entry_situation, "content_reaktion": entry_reaktion,
                                         "content_verhalten": entry_verhalten, "date": formatted_date})

        return render_template("neu.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            password_attempt = request.form.get("password")

            if password_attempt == password:
                session["authenticated"] = True
                return render_template("home.html")
            else:
                return render_template("login.html", message="Falsches Passwort!")

        return render_template("login.html", message=None)

    return app

# if __name__ == '__main__':
#    app.run()
