from user import app
from flask import g
import sys
import mysql.connector

db_config = {'user': 'ece1779A1admin',
             'password': 'ece1779pass',
             'host': str(sys.argv[1]),
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


def get_user_id(user):
    cnx = connect_to_database()
    cursor = cnx.cursor()

    query = ("""SELECT id FROM users WHERE login = %s""")

    cursor.execute(query, (user))

    user_id = cursor.id

    cursor.close()
    cnx.close()

    return user_id


# save a set of images
def save_images(user, files):
    cnx = connect_to_database()
    cursor = cnx.cursor()

    user_id = get_user_id(user)

    query = ("""INSERT INTO images (key1, key2, key3, key4, user_id)
                VALUES (%s, %s, %s, %s, %s)""")

    cursor.execute(query, (files[0], files[1], files[2], files[3], user_id))

    cursor.close()
    cnx.close()


# get all of a user's images
def get_images(user):
    cnx = connect_to_database()
    cursor = cnx.cursor()

    user_id = get_user_id(user)

    query = ("""SELECT * FROM images WHERE user_id = %s)""")

    cursor.execute(query, (user_id))

    images = []
    for (key1, key2, key3, key4) in cursor:
        images.append([key1, key2, key3, key4])

    cursor.close()
    cnx.close()

    return images


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
