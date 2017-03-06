import boto3
from manager import db_config
from manager import worker_config

# create ec2 instance from ami with prepared database
# for now we do this manually so we have control of the hostname/public DNS
# db_config.create_ec2_database()

# create first worker instance
worker_config.create_ec2_worker()

# create load balancer

# regester first worker instance with load balancer