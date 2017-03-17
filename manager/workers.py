from manager import app, loadbalancer

from flask import render_template, redirect, url_for
import boto3
import time
from datetime import datetime, timedelta
from operator import itemgetter

from manager import loadbalancer, db

ami_id = 'ami-81d77c97'
instance_type = 't2.micro'
key_name = 'firstAmazonEC2key'
security_group = ['sg-5a25d025', ]


def create_ec2_worker(sql_host=db.db_config['host']):
    ec2 = boto3.resource('ec2')

    # run app on ec2 instance by passing in mySQL server hostname as argument
    userdata = '''#cloud-config
    runcmd:
     - cd /home/ubuntu/Desktop/ece1779/ece1779Assignment1
     - ./venv_linux/bin/python run_user.py {}
    '''.format(sql_host)

    # create the worker instance
    worker_instance = ec2.create_instances(ImageId=ami_id,
                                           InstanceType=instance_type,
                                           MinCount=1,
                                           MaxCount=1,
                                           KeyName=key_name,
                                           UserData=userdata,
                                           SecurityGroupIds=security_group,
                                           Monitoring={'Enabled': True}
                                           )[0]
    time.sleep(10)
    tags = [
        {
            'Key': 'Role',
            'Value': 'worker'
        },
    ]
    worker_instance.create_tags(
        Tags=tags
    )

    # regester worker instance with load balancer
    elb = boto3.client('elb')
    elb.register_instances_with_load_balancer(LoadBalancerName=loadbalancer.elb_name,
                                              Instances=[{
                                                  'InstanceId': worker_instance.id
                                              }]
                                              )
    time.sleep(10)

    return worker_instance


def get_worker_utilization(id):
    client = boto3.client('cloudwatch')

    metric_name = 'CPUUtilization'

    #    CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn,
    #    NetworkPacketsOut, DiskWriteBytes, DiskReadBytes, DiskWriteOps,
    #    DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed,
    #    StatusCheckFailed_Instance, StatusCheckFailed_System

    namespace = 'AWS/EC2'
    statistic = 'Average'  # could be Sum,Maximum,Minimum,SampleCount,Average

    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=2 * 60),  # go two minutes back
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=['Average', 'Maximum'],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    return cpu


def get_worker_cpu_utilization(id):
    cpu = get_worker_utilization(id)
    max_cpu = 0
    for point in cpu['Datapoints']:
        max_cpu = max(max_cpu, point['Maximum'])

    return max_cpu


def grow_pool():
    ec2 = boto3.resource('ec2')

    # first check that there isn't already a worker being fired up
    all_ec2_instances = ec2.instances.all()
    for instance in all_ec2_instances:
        if instance.tags is not None:
            for tag in instance.tags:
                if tag['Key'] == 'Role' \
                        and tag['Value'] == 'worker' \
                        and instance.state.get('Name') == 'pending':
                    print('worker already being created')
                    return

    # fire up another worker
    print("creating new worker...\n")
    create_ec2_worker(db.db_config['host'])

    return


def shrink_pool():
    ec2 = boto3.resource('ec2')
    elb = boto3.client('elb')

    # get all worker instances registered to the load balancer
    instances = loadbalancer.get_all_instances()

    # find quietest instance, and mark it for execution
    instance_to_kill = None
    min_cpu = 100
    for instance in instances:

        # first make sure instance is in service
        instance_state = loadbalancer.get_health_status(instance.id)
        if instance_state != 'InService':
            continue

        cpu = get_worker_utilization(instance.id)
        for point in cpu['Datapoints']:
            if point['Maximum'] < min_cpu:
                min_cpu = point['Maximum']
                instance_to_kill = instance

    if instance_to_kill is not None:
        print("terminating instance " + instance_to_kill.id + "...\n")
        instance_to_kill.terminate()
    else:
        print('did not find an instance to kill\n')

    return


@app.route('/worker_list', methods=['GET'])
def worker_list():
    # get worker instances
    instances = loadbalancer.get_all_instances()

    # get instances health (InService/OutOfService)
    instances_health = []
    for instance in instances:
        instances_health.append(loadbalancer.get_health_status(instance.id))

    # get instances cpu utilization
    instances_cpu_utilization = []
    for instance in instances:
        instances_cpu_utilization.append(get_worker_cpu_utilization(instance.id))

    return_value = zip(instances, instances_health, instances_cpu_utilization)

    return render_template('workers/list.html',
                           page_header="Worker Pool",
                           instances=return_value)


@app.route('/worker_list/grow', methods=['POST'])
def grow_pool_button():
    create_ec2_worker()

    return redirect(url_for('worker_list'))


@app.route('/worker_list/shrink', methods=['POST'])
def shrink_pool_button():
    shrink_pool()

    return redirect(url_for('worker_list'))
