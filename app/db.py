from app import app
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


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()