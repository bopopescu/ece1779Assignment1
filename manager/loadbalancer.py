from manager import app

import boto3

elb_name = 'ece1779-loadbalancer'
worker_listeners = [{
    'Protocol': 'HTTP',
    'LoadBalancerPort': 80,
    'InstanceProtocol': 'HTTP',
    'InstancePort': 5000
}]
availability_zones = [
    'us-east-1a',
    'us-east-1b',
    'us-east-1c',
    'us-east-1d',
    'us-east-1e'
]
security_group = ['sg-48be4137', ]
health_check = {
    'Target': 'HTTP:5000/',
    'Interval': 10,
    'Timeout': 9,
    'UnhealthyThreshold': 5,
    'HealthyThreshold': 2
}


def create_loadbalancer():
    elb = boto3.client('elb')
    elb.create_load_balancer(LoadBalancerName=elb_name,
                             Listeners=worker_listeners,
                             AvailabilityZones=availability_zones,
                             SecurityGroups=security_group
                             )
    # configure health check
    elb.configure_health_check(LoadBalancerName=elb_name,
                               HealthCheck=health_check
                               )

    elb_description = elb.describe_load_balancers(LoadBalancerNames=[elb_name])
    loadbalancer_host = elb_description.get('LoadBalancerDescriptions')[0].get('DNSName')
    print('load balancer up and running on: ' + loadbalancer_host)

    return loadbalancer_host


def get_all_instances():
    ec2 = boto3.resource('ec2')
    elb = boto3.client('elb')

    # get all worker instances registered to the load balancer
    instances_list = elb.describe_load_balancers(
        LoadBalancerNames=[
            elb_name,
        ]
    )['LoadBalancerDescriptions'][0]['Instances']

    instances = []
    for instance_dict in instances_list:
        instances.append(ec2.Instance(instance_dict['InstanceId']))

    return instances


def get_health_status(id):
    elb = boto3.client('elb')

    instance_state = elb.describe_instance_health(
        LoadBalancerName=elb_name,
        Instances=[
            {
                'InstanceId': id
            },
        ]
    )['InstanceStates'][0]['State']

    return instance_state


@app.route('/loadbalancer', methods=['GET'])
def lb_dns():
    elb = boto3.client('elb')

    loadbalancer_dns = elb.describe_load_balancers(
        LoadBalancerNames=[
            elb_name,
        ])['LoadBalancerDescriptions'][0]['DNSName']
    return loadbalancer_dns
