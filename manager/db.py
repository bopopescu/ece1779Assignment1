from manager import app, db

import boto3
from flask import g
import sys
import mysql.connector

# ec2 ami image with database already set up
ami_id = 'ami-b8d175ae'
instance_type = 't2.micro'
key_name = 'firstAmazonEC2key'
security_group = ['sg-f23cc98d', ]

db_config = {'user': 'ece1779A1admin',
             'password': 'ece1779pass',
             'host': 'ec2-54-197-212-10.compute-1.amazonaws.com',
             'database': 'ece1779a1'
             }


def create_ec2_database():
    ec2_db_instances = boto3.resource('ec2')
    return ec2_db_instances.create_instances(ImageId=ami_id,
                                             InstanceType=instance_type,
                                             MinCount=1,
                                             MaxCount=1,
                                             KeyName=key_name,
                                             SecurityGroupIds=security_group,
                                             Monitoring={'Enabled': True}
                                             )


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
