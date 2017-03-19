from manager import app

from flask import request, render_template, redirect, url_for, session, g
import mysql.connector
from manager.db import get_db

app.secret_key = '\x91b\x8d\xfe\x16\xf5\x15\xd0\xee\xb7ZBe\xe7\x17\xc9Cc\x1cy3\x8f\x86\x84\xc7=\x9c2\x94\xa7YE8\x05'


@app.route('/login', methods=['GET', 'POST'])
# take user to login page or login the user
def login():
    # if user is already logged in (already has a session), go back to index
    if 'username' in session:
        return redirect(url_for('index'))
    else:
        # if method=GET take user to login page
        if request.method == 'GET':
            return render_template('login/login.html',
                                   page_header="Login")
        # if method=POST log the user in
        elif request.method == 'POST':

            provided_username = request.form.get('username')
            provided_password = request.form.get('password')

            # look up the user's password from the users table using username

            # connect to the database
            admin_username = "admin"
            admin_password = "ece1779a1pass"

            # if user is not admin, return an error message
            if provided_username != admin_username:
                return render_template('login/login.html',
                                       page_header="Login",
                                       error_msg="That user does not have access to this page",
                                       username=request.form.get('username'))
            # if password doesn't match, return an error message and reload login page
            elif provided_password != admin_password:
                return render_template('login/login.html',
                                       page_header="Login",
                                       error_msg="Wrong password",
                                       username=request.form.get('username'))
            else:
                session['username'] = provided_username
                return redirect(url_for('index'))


@app.route('/logout', methods=['GET'])
# log the user out
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
# let the user register for a new username and password
def register():
    # if method=GET take user to login page
    if request.method == 'GET':
        return render_template('login/register.html',
                               page_header="Register")
    # if method=POST create a new username and password row in the users table
    elif request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        # do validation on page

        # check if user already exists
        cnx = get_db()
        cursor = cnx.cursor()
        query = '''
                SELECT login FROM users
                WHERE login = %s
                '''
        cursor.execute(query, (username,))
        if cursor.fetchone() is not None:
            return render_template('login/register.html',
                                   page_header="Login",
                                   error_msg="Username already exits",
                                   username=request.form.get('username'))

        # if all good, insert new user into users table
        query = '''
                INSERT INTO users(login, password)
                VALUES (%s,%s)'''
        cursor.execute(query, (username, password))
        cnx.commit()

        return redirect(url_for('login'), code=307)
