import boto3
import time

from manager import loadbalancer

ami_id = 'ami-b6e340a0'
instance_type = 't2.micro'
key_name = 'firstAmazonEC2key'
security_group = ['sg-5a25d025', ]


def create_ec2_worker(sql_host):
    ec2 = boto3.resource('ec2')

    # run app on ec2 instance by passing in mySQL server hostname as argument
    userdata = '''#cloud-config
    runcmd:
     - cd /home/ubuntu/Desktop/ece1779/ece1779Assignment1
     - ./venv_linux/bin/python ece1779Assignment1.py {}
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
    time.sleep(1)
    worker_instance.create_tags(
        Tags=[
                {
                    'Key': 'Role',
                    'Value': 'worker'
                },
        ]
    )

    # regester worker instance with load balancer
    elb = boto3.client('elb')
    elb.register_instances_with_load_balancer(LoadBalancerName=loadbalancer.elb_name,
                                              Instances=[{
                                                  'InstanceId': worker_instance.id
                                              }]
                                              )

    return worker_instance
