from flask import Flask, render_template, url_for
import requests
import json

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/map")
def map_page():
    return render_template("map.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)