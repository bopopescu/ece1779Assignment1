import boto3
import time
from manager import db
from manager import worker
from manager import loadbalancer

if __name__ == '__main__':

    # create ec2 resource
    ec2 = boto3.resource('ec2')

    # create database server
    db_instance = db.create_ec2_database()[0]
    # wait for db server instance to be running so we're sure we can get the public dns
    time.sleep(1)
    while list(ec2.instances.filter(InstanceIds=[db_instance.id]))[0].state.get('Name') != 'running':
        time.sleep(0.1)
    sql_host = list(ec2.instances.filter(InstanceIds=[db_instance.id]))[0].public_dns_name
    print('sql server up and running on: ' + sql_host)

    # create first worker instance, passing in the name of the db server hostname
    worker1_instance = worker.create_ec2_worker(sql_host=sql_host)[0]
    time.sleep(1)
    while list(ec2.instances.filter(InstanceIds=[worker1_instance.id]))[0].state.get('Name') != 'running':
        time.sleep(0.1)
    worker_host = list(ec2.instances.filter(InstanceIds=[worker1_instance.id]))[0].public_dns_name
    print('worker up and running on: ' + worker_host)

    # create load balancer
    elb = boto3.client('elb')
    loadbalancer.create_loadbalancer()
    elb_description = elb.describe_load_balancers(LoadBalancerNames=[loadbalancer.elb_name])
    loadbalancer_host = elb_description.get('LoadBalancerDescriptions')[0].get('DNSName')
    print('load balancer up and running on: ' + loadbalancer_host + ':5000')

    # regester first worker instance with load balancer
    elb.register_instances_with_load_balancer(LoadBalancerName=loadbalancer.elb_name,
                                              Instances=[{
                                                  'InstanceId': worker1_instance.id
                                              }]
                                              )

    # wait for user to type 'stop'
    user_cmd = input("type 'stop' to end manager: ")

    # clean up
    if user_cmd == 'stop':
        elb.delete_load_balancer(LoadBalancerName=loadbalancer.elb_name)
        all_ec2_instances = ec2.instances.all()
        for instance in all_ec2_instances:
            instance.terminate()
