from app import app

from flask import request, render_template, redirect, url_for, session, g
import mysql.connector
from app.db import get_db

app.secret_key = '\t\x9e\xcc\\\xbf\x99U{"\xe5p\xb4\x18\xb7N\xb8%q\xaa\xe5\xd4\x84\xbb\xe8'


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
            cnx = get_db()
            cursor = cnx.cursor()

            # sanitize sql query (provided_username)
            # todo

            # query the database for the password
            query = "SELECT * FROM users WHERE login = %s"
            cursor.execute(query, (provided_username,))

            # now get the password from the cursor
            first_row = cursor.fetchone()

            # if user doesn't exist, return an error message and reload login page
            if first_row is None:
                return render_template('login/login.html',
                                       page_header="Login",
                                       error_msg="No such username",
                                       username=request.form.get('username'))
            else:
                true_password = first_row[2]

            # if password matches, create a session for the user
            if provided_password == true_password:
                session['username'] = provided_username
                return redirect(url_for('index'))
            # if password doesn't match, return an error message and reload login page
            else:
                return render_template('login/login.html',
                                       page_header="Login",
                                       error_msg="Wrong password",
                                       username=request.form.get('username'))


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
