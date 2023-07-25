import os
from flask import (Flask, render_template, request, flash, session, redirect, jsonify)
from model import connect_to_db, db

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]



@app.route('/')
def index():

    return render_template("index.html")



if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)