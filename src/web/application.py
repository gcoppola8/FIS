""" This is the main module for the Flask webserver """
import functools

from flask import Flask, render_template, request, redirect, session, Response, url_for
import json
import requests
import time
import pyDes
from threading import Thread
import logging

from sys import path

path.append('..')
from core.Authorization import Authorizer, AuthError
from core.CaseService import CaseService
from data import Case, User
from data.CaseRepository import CaseRepository

# Create Flask instance and set configurations
from web.authorization import get_user, DefaultAuthorizer

app = Flask(__name__)
app.secret_key = '1@#rTb47BK"_9'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # Set session cookie to 30mins

# Set up separate filehandler and formatter for Flask logger: app.logger
# so that ceratin logs can be logged to a log file
format2 = '%(levelname)s:%(asctime)s%(message)s'
handler2 = logging.FileHandler('log.log', mode='a')
handler2.setLevel(logging.WARNING)
formatter2 = logging.Formatter(format2)
handler2.setFormatter(formatter2)
app.logger.addHandler(handler2)
case_service = CaseService(CaseRepository(), DefaultAuthorizer())

# Instantiate encryption object
encryptor = pyDes.triple_des("VeRy$ecret#1#3#5", pad=".")

# Initiate global dictionary to temporarily store authentication
# details until a user session is created.
logged_in_users_flag = {}


def login_required(view):
    """ Checks authorisation """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        try:
            if session['user_auth']:
                return view(**kwargs)
            else:
                return redirect(url_for('login'))
        except KeyError:
            return redirect(url_for('login'))

    return wrapped_view

@app.errorhandler(AuthError)
def forbidden_op(e):
    """ Handles exception raised for unauthorised activity """
    name = session["user_auth"][0]
    log_message = ' ' + name + ' failed to log in'
    log_thread = Thread(target=app.logger.warning, args=(log_message,))
    log_thread.start()
    return 'Forbidden Operation', 403


# Initial login URL logic follows
@app.route("/", methods=["GET", "POST"])
def login():
    """
        The home page route function displays a login page containing
        a username and password input, then processes the submitted login
        details and creates a unique user session with a related authorisation
        level.
    """

    global logged_in_users_flag
    msg = request.method

    if msg == "GET":
        if request.args.get('message'):
            return render_template("login.html", message=request.args.get('message'))
        else:
            return render_template("login.html")

    elif msg == "POST":
        try:
            name = request.form.get("name")
            password = request.form.get("password")
            encrypted_password = (encryptor.encrypt(password))
            # The encytped password is converted to a list of integers to make it
            # JON serialisable as it is returned as a bytestring.
            # The list is put into another list also containing the username entered.
            login = [name, list(encrypted_password)]
            login_json = json.dumps(login)

            # Send to the Authentication microservice.
            http_header = {'Content-Type': 'application/json'}
            reply = requests.post('http://localhost:5005/login', headers=http_header, data=login_json)
            # Sleep the code so that any communication delay won't create
            # a fault as the microservice responds to the "log_users" URL below.
            time.sleep(4)
        except:
            return render_template("login.html", message="Login failed. Please try again")

        # Check the values returned from the Authentication microservice
        try:
            # Check the flag received from the microservice and temporarily
            # stored in the logged_in_users_flag dictionary 
            if ((logged_in_users_flag[name] == 1) or
                    (logged_in_users_flag[name] == 2) or
                    (logged_in_users_flag[name] == 3)):

                # Create a session and assign the user's name and auth level to it 
                session['user_auth'] = [name, logged_in_users_flag[name]]
                del logged_in_users_flag[name]
                # Log login in a separate thread
                log_message = session['user_auth'][0] + ' logged in at auth level of: ' + \
                              str(session['user_auth'][1])
                log_thread = Thread(target=app.logger.warning, args=(log_message,))
                log_thread.start()
                return redirect("/cases")
            elif logged_in_users_flag[name] == "F":
                log_message = ' ' + name + ' failed to log in'
                log_thread = Thread(target=app.logger.warning, args=(log_message,))
                log_thread.start()
                return render_template("login.html", message="Login Failed. Please try again")
            elif logged_in_users_flag[name] == "FNN":
                log_message = ' ' + name + ' failed to log in'
                log_thread = Thread(target=app.logger.warning, args=(log_message,))
                log_thread.start()
                return render_template("login.html", message="Username does not exist. Please try again")

            # For future to lock a user's profile
            elif logged_in_users_flag[name] == "F1":
                # **Log login outcome**
                return render_template("login.html", message="Incorrect password. Please try again. two more attempts")
            elif logged_in_users_flag[name] == "F2":
                # **Log login outcome**
                return render_template("login.html", message="Incorrect password. Please try again. one more attempts")
            elif logged_in_users_flag[name] == "F3":
                # **Log login outcome**
                return render_template("login.html",
                                       message="Incorrect password. Your account has been locked please contact admin")

        except:
            return render_template("login.html", message="Login failed. Please try again.")


@app.route("/update_users", methods=["POST"])
def log_users():
    ''' Creates an entry to be stored temporarily in a global dictionary. '''

    global logged_in_users_flag
    # Receive response from Authenticate microservice
    new_user = request.json
    logged_in_users_flag[new_user[0]] = new_user[1]
    return "successful"


# Options URL logic
@app.route("/options", methods=["GET", "POST"])
@login_required
def options():
    """
        The options page provides an initial means to the user
        to navigate to the required service.
    """


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """
        The create page allows a user to create a case
        by first entering its related metadata.
    """

    if request.method == 'GET':
        case_service.authorize_create()
        return render_template("create.html")
    elif request.method == 'POST':
        logged_user: User = get_user()
        case = Case(logged_user.user_id, name=request.form['name'], description=request.form['description'])
        case_service.create(case)

        return render_template("cases.html")


# Search URL logic
@app.route("/cases", methods=["GET", "POST"])
@login_required
def cases():
    """
        The search page allows a user to enter a case number,
        creation date, or/and name substring to reveal the cases 
        whose values contain the entered ones.       
    """
    page_size = request.args.get('page_size', 1000, int)
    page_number = request.args.get('page_number', 1, int)
    cases = case_service.find_all(page_size=page_size, page_number=page_number)
    return render_template("cases.html", cases=cases)


# Edit URL logic
@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    """
        The edit case page requires a user to enter a case
        number for a case to edit then redirects to the
        specific case.
    """
    if request.method == 'GET':
        case_id = request.args.get('case_id')
        case = case_service.find_by_id(case_id)

        return render_template("edit.html", case=case)

    elif request.method == 'POST':
        case_id = request.form['case_id']
        case = case_service.find_by_id(case_id)
        case.name = request.form['name']
        case.description = request.form['description']

        return redirect(url_for("cases"))

@app.route("/delete", methods=['GET'])
@login_required
def delete():
    """
        Delete endpoint
    """
    case_id = request.args.get('case_id')
    case = case_service.find_by_id(case_id)
    case_service.archive(case)
    return redirect(url_for("cases"))


# Logout URL logic
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """
        To log out.
    """
    # **Log logout**

    try:
        name = session["user_auth"][0]
        name_json = json.dumps(name)
        # Send to the Authentication microservice to process and update database.
        http_header = {'Content-Type': 'application/json'}
        reply = requests.post('http://localhost:5005/logout', headers=http_header, data=name_json)
        # Remove session dictionary from server
        username = session['user_auth'][0]
        session.pop('user_auth', None)
        # Log changes
        log_message = username + ' logged out'
        log_thread = Thread(target=app.logger.warning, args=(log_message,))
        log_thread.start()
        return redirect(url_for("login"))
    except:
        return "logout unsuccessful"


if __name__ == '__main__':
    # Run the Flask webserver
    app.run(port=5000)
