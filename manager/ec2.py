from manager import app, workers, db

from flask import render_template, redirect, url_for, request

import boto3
from datetime import datetime, timedelta
from operator import itemgetter


@app.route('/ec2_list', methods=['GET'])
def ec2_list():

    ec2 = boto3.resource('ec2')
    elb = boto3.client('elb')

    instances = ec2.instances.all()

    return render_template('ec2_workers/list.html',
                           title='EC2 Instances',
                           instances=instances)


@app.route('/ec2_workers/create', methods=['POST'])
def ec2_create():

    ec2 = boto3.resource('ec2')
    workers.create_ec2_worker(sql_host=db.db_config['host'])

    return redirect(url_for('ec2_list'))


@app.route('/ec2_example/<id>', methods=['GET'])
def ec2_view(id):
    ec2 = boto3.resource('ec2')

    instance = ec2.Instance(id)

    client = boto3.client('cloudwatch')

    metric_name = 'CPUUtilization'

    #    CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn,
    #    NetworkPacketsOut, DiskWriteBytes, DiskReadBytes, DiskWriteOps,
    #    DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed,
    #    StatusCheckFailed_Instance, StatusCheckFailed_System

    namespace = 'AWS/EC2'
    statistic = 'Average'                   # could be Sum,Maximum,Minimum,SampleCount,Average

    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    cpu_stats = []

    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        cpu_stats.append([time,point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))

    statistic = 'Sum'  # could be Sum,Maximum,Minimum,SampleCount,Average

    network_in = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkIn',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    net_in_stats = []

    for point in network_in['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        net_in_stats.append([time,point['Sum']])

    net_in_stats = sorted(net_in_stats, key=itemgetter(0))

    network_out = client.get_metric_statistics(
        Period=5 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkOut',
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    net_out_stats = []

    for point in network_out['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        net_out_stats.append([time,point['Sum']])

        net_out_stats = sorted(net_out_stats, key=itemgetter(0))

    return render_template("ec2_workers/view.html", title="Instance Info",
                           instance=instance,
                           cpu_stats=cpu_stats,
                           net_in_stats=net_in_stats,
                           net_out_stats=net_out_stats)


@app.route('/ec2_workers/start/<id>', methods=['POST'])
def ec2_start(id):

    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=[id]).start()

    return redirect(url_for('ec2_list'))


@app.route('/ec2_workers/stop/<id>', methods=['POST'])
def ec2_stop(id):

    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=[id]).stop()

    return redirect(url_for('ec2_list'))


@app.route('/ec2_workers/delete/<id>', methods=['POST'])
def ec2_destroy(id):

    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=[id]).terminate()

    return redirect(url_for('ec2_list'))
