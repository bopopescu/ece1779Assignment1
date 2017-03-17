import boto3
import time
import statistics

from manager import workers, db, loadbalancer

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
        instances = loadbalancer.get_all_instances()

        cpu_utilizations = []
        print('worker instances: ')
        for instance in instances:

            # first make sure instance is in service
            instance_state = loadbalancer.get_health_status(instance.id)
            if instance_state != 'InService':
                outofservice_workers += 1
                print(instance.id + ' is ' + instance_state)
                continue
            else:
                running_workers += 1


            cpu = workers.get_worker_utilization(instance.id)
            max_cpu = 0
            for point in cpu['Datapoints']:
                max_cpu = max(max_cpu, point['Maximum'])
            print(instance.id + ": max cpu: " + str(max_cpu))
            cpu_utilizations.append(max_cpu)
            if max_cpu > high_cpu_threshold:
                busy_workers += 1
            elif max_cpu < low_cpu_threshold:
                quiet_workers += 1

        average_utilization = statistics.mean(cpu_utilizations)

        print('\n')
        print('running workers:        ' + str(running_workers))
        print('    quiet workers:      ' + str(quiet_workers))
        print('    busy workers:       ' + str(busy_workers))
        print('out of service workers: ' + str(outofservice_workers))
        print('average utilization:    ' + str(average_utilization))
        print('\n')

        # if there are no running workers, start one
        if running_workers == 0:
            print('starting first worker...')
            workers.create_ec2_worker(db.db_config['host'])
            time.sleep(30)

        if average_utilization > high_cpu_threshold:
            print('going to grow pool...')
            workers.grow_pool()
        elif average_utilization < low_cpu_threshold:
            if running_workers == 1:
                print('only one worker, not shrinking')
            else:
                print('going to shrink pool...')
                workers.shrink_pool()

        # if there are quiet workers and no busy workers, shrink the pool
        #if quiet_workers >= 1 and busy_workers == 0:
        #    if running_workers == 1:
        #        print('only one worker, not shrinking')
        #    elif running_workers > 1:
        #        print('going to shrink pool...')
        #        workers.shrink_pool()
        # if there are busy workers and no quiet or starting-up workers, grow the pool
        #elif busy_workers >= 1 and quiet_workers == 0 and outofservice_workers == 0:
        #    print('going to grow pool...')
        #    workers.grow_pool()

        print('finished monitor cycle\n')
        time.sleep(10)
    return
