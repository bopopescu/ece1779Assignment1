import boto3

# ec2 ami image provided by professor
ami_id = 'ami-e3f432f5'
instance_type = 't2.micro'
key_name = 'firstAmazonEC2key'


def create_ec2_worker():
    ec2_db_instance = boto3.resource('ec2')
    ec2_db_instance.create_instance(ImageId=ami_id,
                                    InstanceType=instance_type,
                                    MinCount=1,
                                    MaxCount=1,
                                    KeyName=key_name,
                                    Monitoring={'Enabled': True}
                                    )
    return 0
