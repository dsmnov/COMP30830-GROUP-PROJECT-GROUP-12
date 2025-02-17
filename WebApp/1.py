from flask import Flask, render_template
import requests
import json

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("ABC.html")

app.run(host="0.0.0.0", port=80)