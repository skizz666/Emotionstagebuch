import datetime
import os
from flask import Flask, render_template, request
from pymongo import MongoClient
from dotenv import load_dotenv
import gunicorn


load_dotenv()


def create_app():
    app = Flask(__name__)
    client = MongoClient(os.getenv("MONGODB_URI"))
    app.db = client.emotionstagebuch

    entries = []

    @app.route("/", methods=["GET", "POST"])
    def home():

        entries_with_date = [
            (
                entry["content_situation"],
                entry["content_reaktion"],
                entry["content_verhalten"],
                entry["date"],
                datetime.datetime.strptime(entry["date"], "%d.%m.%Y, %H:%M").strftime("%b, %d"),
            )
            for entry in app.db.emotionen.find({})
        ]
        sorted_entries = sorted(entries_with_date, key=lambda x: x[3], reverse=True)

        return render_template("home.html", entries=sorted_entries)

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

    return app

# if __name__ == '__main__':
#    app.run()
