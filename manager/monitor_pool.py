import boto3
import time

from manager import worker, db


def background_monitor():
    ec2 = boto3.resource('ec2')

    while True:
        all_ec2_instances = ec2.instances.all()
        for instance in all_ec2_instances:
            if instance.tags is not None:
                for tag in instance.tags:
                    if tag['Key'] == 'Role' \
                            and tag['Value'] == 'worker' \
                            and instance.state.get('Name') == 'running':
                        cpu = worker.get_worker_utilization(instance.id)
                        max_cpu = 0
                        min_cpu = 100
                        for point in cpu['Datapoints']:
                            max_cpu = max(max_cpu, point['Maximum'])
                            min_cpu = min(min_cpu, point['Minimum'])
                            avg_cpu = point['Average']
                        print(
                            instance.id + ": max: " + str(max_cpu) + " min: " + str(min_cpu) + " avg: " + str(avg_cpu))
                        if max_cpu > 30:
                            grow_pool()
                        elif max_cpu < 10:
                            shrink_pool()
    time.sleep(10)
    return


def grow_pool():
    # first check that there isn't already a worker being fired up
    ec2 = boto3.resource('ec2')
    all_ec2_instances = ec2.instances.all()
    for instance in all_ec2_instances:
        if instance.tags is not None:
            for tag in instance.tags:
                if tag['Key'] == 'Role' \
                        and tag['Value'] == 'worker' \
                        and instance.state.get('Name') == 'pending':
                    return

    # only grow if there is no other instance below 10%
    ec2 = boto3.resource('ec2')
    all_ec2_instances = ec2.instances.all()
    for instance in all_ec2_instances:
        if instance.tags is not None:
            for tag in instance.tags:
                if tag['Key'] == 'Role' \
                        and tag['Value'] == 'worker' \
                        and instance.state.get('Name') == 'running':
                    cpu = worker.get_worker_utilization(instance.id)
                    for point in cpu['Datapoints']:
                        if point['Maximum'] < 10:
                            return

    # fire up another worker
    print("creating new worker")
    worker.create_ec2_worker(db.db_config['host'])
    return


def shrink_pool():
    # only shrink if there is no other instance above 60%
    ec2 = boto3.resource('ec2')
    all_ec2_instances = ec2.instances.all()
    for instance in all_ec2_instances:
        if instance.tags is not None:
            for tag in instance.tags:
                if tag['Key'] == 'Role' \
                        and tag['Value'] == 'worker' \
                        and instance.state.get('Name') == 'running':
                    cpu = worker.get_worker_utilization(instance.id)
                    for point in cpu['Datapoints']:
                        if point['Maximum'] > 30:
                            return

    # find quietest instance, and mark it for execution
    instance_to_kill = None
    min_cpu = 100
    for instance in all_ec2_instances:
        if instance.tags is not None:
            for tag in instance.tags:
                if tag['Key'] == 'Role' \
                        and tag['Value'] == 'worker' \
                        and instance.state.get('Name') == 'running':
                    cpu = worker.get_worker_utilization(instance.id)
                    for point in cpu['Datapoints']:
                        if point['Maximum'] < min_cpu:
                            instance_to_kill = instance

    # don't kill it if it's the first worker
    is_first_worker = False
    for tag in instance_to_kill.tags:
        if tag['Key'] == 'First Worker' and tag['Value'] == 'true':
            is_first_worker = True
    if not is_first_worker:
        print("killing " + instance.id)
        instance_to_kill.terminate()
    return
