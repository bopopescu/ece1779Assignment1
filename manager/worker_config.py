import boto3

# ec2 ami image provided by professor
# when app is implemented, use our own image with app on it
ami_id = 'ami-e3f432f5'
instance_type = 't2.micro'
key_name='firstAmazonEC2key'

def create_ec2_worker():
    ec2_db_instance = boto3.resource('ec2')
    # will need to run the following with userdata to initialize app
    userdata = '''#cloud-config
    runcmd:
     - cd ~/Documents/ece1779/ece1779Assignment1
     - ./venv/bin/python ece1779Assignment1.py
    '''
    ec2_db_instance.create_instance(ImageId=ami_id,
                                    InstanceType=instance_type,
                                    MinCount=1,
                                    MaxCount=1,
                                    KeyName=key_name,
                                    userdata=userdata,
                                    Monitoring={'Enabled': True}
                                    )
    return 0
