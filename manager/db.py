import boto3

# ec2 ami image with database already set up
ami_id = 'ami-b8d175ae'
instance_type = 't2.micro'
key_name = 'firstAmazonEC2key'
security_group = ['sg-f23cc98d',]

# configuration of database on the prepared ami
db_config = {'user': 'ece1779A1admin',
             'password': 'ece1779pass',
             'host': 'ec2-54-161-36-174.compute-1.amazonaws.com',
             'database': 'ece1779a1'
             }


def create_ec2_database():
    ec2_db_instance = boto3.resource('ec2')
    return ec2_db_instance.create_instances(ImageId=ami_id,
                                            InstanceType=instance_type,
                                            MinCount=1,
                                            MaxCount=1,
                                            KeyName=key_name,
                                            SecurityGroupIds=security_group,
                                            Monitoring={'Enabled': True}
                                            )
