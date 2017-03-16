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
    ec2 = boto3.resource('ec2')

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


def grow_pool():
    ec2 = boto3.resource('ec2')
    elb = boto3.client('elb')

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

    # only grow if there is no other instance below low_cpu_threshold
    # get all worker instances registered to the load balancer
    loadbalancer_response = elb.describe_load_balancers()
    loadbalancer_descriptions = loadbalancer_response['LoadBalancerDescriptions']
    for loadbalancer_description in loadbalancer_descriptions:
        instances_list = loadbalancer_description['Instances']

    for instance_dict in instances_list:
        instance_id = instance_dict['InstanceId']
        instance = ec2.Instance(instance_id)

        # first make sure instance is in service
        instance_running = False
        instance_health = elb.describe_instance_health(
            LoadBalancerName=loadbalancer.elb_name,
            Instances=[
                {
                    'InstanceId': instance.id
                },
            ]
        )
        instance_states = instance_health['InstanceStates']
        for instance_state in instance_states:
            if instance_state['State'] == 'InService':
                instance_running = True
        if instance_running is not True:
            continue

            cpu = worker.get_worker_utilization(instance.id)
            for point in cpu['Datapoints']:
                if point['Maximum'] < low_cpu_threshold:
                    print('quiet worker already exists, not growing\n')
                    return

    # fire up another worker
    print("creating new worker...\n")
    create_ec2_worker(db.db_config['host'])
    # wait two and a half minutes for worker to start and become InService
    # Pool monitor ignores OutOfService instances
    # (we don't know if it's OutOfService because it hasn't started yet
    # or because it's still starting up)
    # Therefore, we don't want the pool monitor to start another worker while
    # this one is starting up
    #time.sleep(150)

    return


def shrink_pool():
    ec2 = boto3.resource('ec2')
    elb = boto3.client('elb')

    # get all worker instances registered to the load balancer
    loadbalancer_response = elb.describe_load_balancers()
    loadbalancer_descriptions = loadbalancer_response['LoadBalancerDescriptions']
    for loadbalancer_description in loadbalancer_descriptions:
        instances_list = loadbalancer_description['Instances']

    # find quietest instance, and mark it for execution
    instance_to_kill = None
    min_cpu = 100
    for instance_dict in instances_list:
        instance_id = instance_dict['InstanceId']
        instance = ec2.Instance(instance_id)

        # first make sure instance is in service
        instance_running = False
        instance_health = elb.describe_instance_health(
            LoadBalancerName=loadbalancer.elb_name,
            Instances=[
                {
                    'InstanceId': instance.id
                },
            ]
        )
        instance_states = instance_health['InstanceStates']
        for instance_state in instance_states:
            if instance_state['State'] == 'InService':
                instance_running = True
        if instance_running is not True:
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
        print('no instance to kill\n')

    return
