from flask import render_template, redirect, url_for
from manager import app

import boto3
import time
from manager import db
from manager import worker
from manager import loadbalancer


@app.route('/start')
def start():
    # create load balancer
    elb = boto3.client('elb')
    loadbalancer_host = loadbalancer.create_loadbalancer()

    # create ec2 resource so we can get information (hostnames) about the instances
    ec2 = boto3.resource('ec2')

    # create first worker instance, passing in the name of the db server hostname
    sql_host = db.db_config.get('host')
    worker1_instance = worker.create_ec2_worker(sql_host=sql_host)
    # get the hostname of the worker instance
    time.sleep(1)
    worker_host = list(ec2.instances.filter(InstanceIds=[worker1_instance.id]))[0].public_dns_name

    return render_template("admin/start.html",
                           page_header="Start complete",
                           sql_host=sql_host,
                           worker1_host=worker_host + ':5000',
                           loadbalancer_host=loadbalancer_host
                           )


@app.route('/start_sql')
def start_sql():
    db.create_ec2_database()
    return redirect(url_for('index'))
