import boto3

# ec2 ami image with database already set up
ami_id = 'ami-b8d175ae'
instance_type = 't2.micro'
key_name = 'firstAmazonEC2key'

# configuration of database on the prepared ami
db_config = {'user': 'ece1779A1admin',
             'password': 'ece1779pass',
             'host': 'ec2-54-161-36-174.compute-1.amazonaws.com',
             'database': 'ece1779a1'
             }


def create_ec2_database():
    ec2_db_instance = boto3.resource('ec2')
    ec2_db_instance.create_instance(ImageId=ami_id,
                                    InstanceType=instance_type,
                                    MinCount=1,
                                    MaxCount=1,
                                    KeyName=key_name,
                                    Monitoring={'Enabled': True}
                                    )
    return 0
