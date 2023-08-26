import os
from flask import (Flask, render_template, request, flash, get_flashed_messages, session, redirect, jsonify)
from model import connect_to_db, db, User
import crud
from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
app.jinja_env.undefined = StrictUndefined



#index
@app.route('/')
def index():

    if "email" in session and "user_id" in session:
        return redirect(f'/dashboard/{session["user_id"]}')

    return render_template("index.html")


#user registration
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    messages = get_flashed_messages()

    if "email" in session and "user_id" in session:
        return redirect(f'/dashboard/{session["user_id"]}')

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = crud.get_user_by_email(email)

        if user:
            flash("Cannot create an account with that email address. Try again.")
        else:
            crud.create_user(email, password)
            flash("Account successfully created! Redirecting to the log in page...", "success")

        return redirect('/registration')

    return render_template("registration.html", messages=messages)


#user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    messages = get_flashed_messages()

    if "email" in session and "user_id" in session:
        return redirect(f'/dashboard/{session["user_id"]}')

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = crud.get_user_by_email(email)

        while user:
            if email == user.email and password == user.password:
                session["email"] = user.email
                session["user_id"] = user.user_id
                return redirect(f'/dashboard/{user.user_id}')
            else:
                flash("Invalid email or password. Try again.")
                return redirect('/login')

    return render_template("login.html", messages=messages)


#user logout
@app.route('/logout', methods=['POST'])
def logout():

    session.clear()
    return redirect('/')


#unique user dashboard
@app.route('/dashboard/<user_id>')
def dashboard(user_id):

    user = crud.get_user_by_id(user_id)

    return render_template("dashboard.html", user=user)



if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)