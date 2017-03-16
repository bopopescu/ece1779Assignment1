from user import app
from flask import g
import sys
import mysql.connector

db_host = ''
try:
    db_host = sys.argv[1]
except IndexError:
    db_host = 'ec2-54-172-237-92.compute-1.amazonaws.com'

db_config = {'user': 'ece1779A1admin',
             'password': 'ece1779pass',
             'host': db_host,
             'database': 'ece1779a1'
             }


# connect to database
def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database']
                                   )


# get singleton database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db


def get_user_id(username):
    cnx = connect_to_database()
    cursor = cnx.cursor()

    query = '''
            SELECT id FROM users WHERE login = %s
            '''

    cursor.execute(query, (username,))

    row = cursor.fetchone()

    if row is not None:
        user_id = row[0]
    else:
        user_id = None

    cursor.close()
    cnx.close()

    return user_id


# save a set of images
def save_images(username, files):
    cnx = connect_to_database()
    cursor = cnx.cursor()

    user_id = get_user_id(username)
    if user_id is None:
        cursor.close()
        cnx.close()
        return

    query = '''
            INSERT INTO images (key1, key2, key3, key4, users_id)
            VALUES (%s, %s, %s, %s, %s)
            '''

    cursor.execute(query, (files[0], files[1], files[2], files[3], user_id))
    cnx.commit()

    cursor.close()
    cnx.close()

    return


# get all of a user's images
def get_images(username):
    cnx = connect_to_database()
    cursor = cnx.cursor()

    user_id = get_user_id(username)
    if user_id is None:
        return None

    query = '''
            SELECT * FROM images WHERE users_id = %s
            '''

    cursor.execute(query, (user_id,))
    rows = cursor.fetchall()
    print(str(rows))

    images = []
    for row in rows:
        images.append([row[1], row[2], row[3], row[4]])

    cursor.close()
    cnx.close()

    print(str(images))
    return images


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
