import boto3
from manager import db
from manager import worker

if __name__ == '__main__':

    # create ec2 instance from ami with prepared database
    # for now we do this manually so we have control of the hostname/public DNS
    ec2 = boto3.resource('ec2')

    db_instances = db.create_ec2_database()
    sql_host = db_instances[0].public_dns_name
    print(sql_host)
    # create first worker instance
    worker.create_ec2_worker(sql_host=sql_host)

    # create load balancer

    # regester first worker instance with load balancer