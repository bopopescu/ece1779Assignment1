import boto3

# ec2 ami image provided by professor
# when app is implemented, use our own image with app on it
ami_id = 'ami-37892e21'
instance_type = 't2.micro'
key_name = 'firstAmazonEC2key'
security_group = 'sg-5a25d025'

def create_ec2_worker(sql_host):
    ec2_db_instance = boto3.resource('ec2')
    # will need to run the following with userdata to initialize app
    # run app on ec2 instance passing in mySQL server hostname as argument
    userdata = '''#cloud-config
    runcmd:
     - cd ~/Documents/ece1779/ece1779Assignment1
     - ./venv/bin/python ece1779Assignment1.py {}
    '''.format(sql_host)
    return ec2_db_instance.create_instances(ImageId=ami_id,
                                    InstanceType=instance_type,
                                    MinCount=1,
                                    MaxCount=1,
                                    KeyName=key_name,
                                    UserData=userdata,
                                    SecurityGroupIds=security_group,
                                    Monitoring={'Enabled': True}
                                    )
