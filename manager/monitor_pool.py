import boto3
import time

from manager import worker, db, loadbalancer

high_cpu_threshold = 40
low_cpu_threshold = 20


def background_monitor():
    ec2 = boto3.resource('ec2')
    elb = boto3.client('elb')

    while True:
        print('starting monitor cycle')

        # count the number of workers
        busy_workers = 0
        quiet_workers = 0
        running_workers = 0
        outofservice_workers = 0

        # get all worker instances registered to the load balancer
        loadbalancer_response = elb.describe_load_balancers()
        loadbalancer_descriptions = loadbalancer_response['LoadBalancerDescriptions']
        for loadbalancer_description in loadbalancer_descriptions:
            instances_list = loadbalancer_description['Instances']

        print('worker instances: ')
        for instance_dict in instances_list:
            instance_id = instance_dict['InstanceId']
            instance = ec2.Instance(instance_id)

            # first make sure instance is in service
            instance_running = False
            instance_health = elb.describe_instance_health(
                LoadBalancerName=loadbalancer.elb_name,
                Instances=[
                    {
                        'InstanceId': instance.id
                    },
                ]
            )
            instance_states = instance_health['InstanceStates']
            for instance_state in instance_states:
                if instance_state['State'] == 'InService':
                    instance_running = True
            if instance_running is not True:
                outofservice_workers += 1
                print(instance.id + ' is ' + str(instance_state['State']))
                continue

            # if it got here, then it is in service
            # now look at it's cpu utilization
            if instance.tags is not None:
                for tag in instance.tags:
                    if tag['Key'] == 'Role' \
                            and tag['Value'] == 'worker' \
                            and instance.state.get('Name') == 'running':
                        running_workers += 1
                        cpu = worker.get_worker_utilization(instance.id)
                        max_cpu = 0
                        for point in cpu['Datapoints']:
                            max_cpu = max(max_cpu, point['Maximum'])
                        print(
                            instance.id + ": max cpu: " + str(max_cpu))
                        if max_cpu > high_cpu_threshold:
                            busy_workers += 1
                        elif max_cpu < low_cpu_threshold:
                            quiet_workers += 1

        print('\n')
        print('running workers:        ' + str(running_workers))
        print('quiet workers:          ' + str(quiet_workers))
        print('busy workers:           ' + str(busy_workers))
        print('out of service workers: ' + str(outofservice_workers))
        print('\n')

        # if there are no running or OutOfService (perhaps starting) workers, start one
        if running_workers + outofservice_workers == 0:
            print('starting first worker...')
            worker.create_ec2_worker(db.db_config['host'])
            time.sleep(150)
        # terminate quiet workers before starting new ones
        if quiet_workers >= 1:
            if running_workers == 1:
                print('only one worker, not shrinking')
            elif running_workers > 1:
                print('going to shrink pool...')
                shrink_pool()
        # if there are no more quiet workers to terminate, grow pool
        elif busy_workers >= 1:
            print('going to grow pool...')
            grow_pool()
        print('finished monitor cycle\n')
        time.sleep(10)
    return


def grow_pool():
    ec2 = boto3.resource('ec2')
    elb = boto3.client('elb')

    # first check that there isn't already a worker being fired up
    all_ec2_instances = ec2.instances.all()
    for instance in all_ec2_instances:
        if instance.tags is not None:
            for tag in instance.tags:
                if tag['Key'] == 'Role' \
                        and tag['Value'] == 'worker' \
                        and instance.state.get('Name') == 'pending':
                    print('worker already being created')
                    return

    # only grow if there is no other instance below low_cpu_threshold
    # get all worker instances registered to the load balancer
    loadbalancer_response = elb.describe_load_balancers()
    loadbalancer_descriptions = loadbalancer_response['LoadBalancerDescriptions']
    for loadbalancer_description in loadbalancer_descriptions:
        instances_list = loadbalancer_description['Instances']

    for instance_dict in instances_list:
        instance_id = instance_dict['InstanceId']
        instance = ec2.Instance(instance_id)

        # first make sure instance is in service
        instance_running = False
        instance_health = elb.describe_instance_health(
            LoadBalancerName=loadbalancer.elb_name,
            Instances=[
                {
                    'InstanceId': instance.id
                },
            ]
        )
        instance_states = instance_health['InstanceStates']
        for instance_state in instance_states:
            if instance_state['State'] == 'InService':
                instance_running = True
        if instance_running is not True:
            continue

            cpu = worker.get_worker_utilization(instance.id)
            for point in cpu['Datapoints']:
                if point['Maximum'] < low_cpu_threshold:
                    print('quiet worker already exists, not growing\n')
                    return

    # fire up another worker
    print("creating new worker...\n")
    worker.create_ec2_worker(db.db_config['host'])
    # wait two and a half minutes for worker to start and become InService
    # Pool monitor ignores OutOfService instances
    # (we don't know if it's OutOfService because it hasn't started yet
    # or because it's still starting up)
    # Therefore, we don't want the pool monitor to start another worker while
    # this one is starting up
    time.sleep(150)

    return


def shrink_pool():
    ec2 = boto3.resource('ec2')
    elb = boto3.client('elb')

    # get all worker instances registered to the load balancer
    loadbalancer_response = elb.describe_load_balancers()
    loadbalancer_descriptions = loadbalancer_response['LoadBalancerDescriptions']
    for loadbalancer_description in loadbalancer_descriptions:
        instances_list = loadbalancer_description['Instances']

    # find quietest instance, and mark it for execution
    instance_to_kill = None
    min_cpu = 100
    for instance_dict in instances_list:
        instance_id = instance_dict['InstanceId']
        instance = ec2.Instance(instance_id)

        # first make sure instance is in service
        instance_running = False
        instance_health = elb.describe_instance_health(
            LoadBalancerName=loadbalancer.elb_name,
            Instances=[
                {
                    'InstanceId': instance.id
                },
            ]
        )
        instance_states = instance_health['InstanceStates']
        for instance_state in instance_states:
            if instance_state['State'] == 'InService':
                instance_running = True
        if instance_running is not True:
            continue

        cpu = worker.get_worker_utilization(instance.id)
        for point in cpu['Datapoints']:
            if point['Maximum'] < min_cpu:
                min_cpu = point['Maximum']
                instance_to_kill = instance

    if instance_to_kill is not None:
        print("terminating instance " + instance_to_kill.id + "...\n")
        instance_to_kill.terminate()
    else:
        print('no instance to kill\n')

    return
