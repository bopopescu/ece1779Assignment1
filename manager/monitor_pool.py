import boto3
import time

from manager import worker, db

high_cpu_threshold = 40
low_cpu_threshold = 10


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
                        if max_cpu > high_cpu_threshold:
                            grow_pool()
                        elif max_cpu < low_cpu_threshold:
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

    # only grow if there is no other instance below low_cpu_threshold
    for instance in all_ec2_instances:
        if instance.tags is not None:
            for tag in instance.tags:
                if tag['Key'] == 'Role' \
                        and tag['Value'] == 'worker' \
                        and instance.state.get('Name') == 'running':
                    cpu = worker.get_worker_utilization(instance.id)
                    for point in cpu['Datapoints']:
                        if point['Maximum'] < low_cpu_threshold:
                            return

    # fire up another worker
    print("creating new worker")
    new_worker = worker.create_ec2_worker(db.db_config['host'])

    # after creating a worker, wait for it to finish being in 'pending' state
#    while new_worker.state.get('Name') != 'running':
#        time.sleep(0.1)

    return


def shrink_pool():
    # only shrink if there is no other instance above high_cpu_threshold
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
                        if point['Maximum'] > high_cpu_threshold:
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
        print("killing " + instance_to_kill.id)
        instance_to_kill.terminate()

    return
