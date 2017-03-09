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
    elb_client = boto3.client('elb')
    elb_client.create_load_balancer(LoadBalancerName=elb_name,
                                    Listeners=worker_listeners,
                                    AvailabilityZones=availability_zones,
                                    SecurityGroups=security_group
                                    )
    # configure health check
    elb_client.configure_health_check(LoadBalancerName=elb_name,
                                      HealthCheck=health_check
                                      )

    # add instances
