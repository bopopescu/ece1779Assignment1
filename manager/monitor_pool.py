import boto3
import time
import statistics

from manager import workers, db, loadbalancer

class PolicyVars(object):
    __instance = None

    def __new__(cls):
        if PolicyVars.__instance is None:
            PolicyVars.__instance = object.__new__(cls)
            # default values. 0 means just grow/shrink by one instance
            PolicyVars.__instance.high_cpu_threshold = 40
            PolicyVars.__instance.low_cpu_threshold = 20
            PolicyVars.__instance.scaling_multiplier = 0
            PolicyVars.__instance.scaling_divisor = 0
        return PolicyVars.__instance


# Store policy variables
global pv
pv = PolicyVars()


def background_monitor():
    print('starting pool monitor')

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

        print('\n')
        print('high thresh: ' + str(pv.high_cpu_threshold))
        print('low thresh:  ' + str(pv.low_cpu_threshold))
        print('divisor:     ' + str(pv.scaling_multiplier))
        print('multiplier:  ' + str(pv.scaling_divisor))
        print('\n')

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

            if max_cpu > pv.high_cpu_threshold:
                busy_workers += 1
            elif max_cpu < pv.low_cpu_threshold:
                quiet_workers += 1

        if not cpu_utilizations:
            average_utilization = 0
        else:
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
            workers.create_ec2_worker()
            time.sleep(30)

        if average_utilization > pv.high_cpu_threshold:
            number_to_grow = 0
            if pv.scaling_multiplier == 0:
                number_to_grow = 1
            else:
                number_to_grow = running_workers * pv.scaling_multiplier
            print('going to grow pool by: ' + str(number_to_grow))
            workers.grow_pool(number_to_grow)
        elif average_utilization < pv.low_cpu_threshold:
            if running_workers == 1:
                print('only one worker, not shrinking')
            else:
                number_to_shrink = 0
                if pv.scaling_divisor == 0:
                    number_to_shrink = 1
                else:
                    number_to_shrink = \
                        min(running_workers - 1,
                            running_workers - running_workers//pv.scaling_divisor)
                print('going to shrink pool by: ' + str(number_to_shrink))
                workers.shrink_pool(number_to_shrink)

        print('finished monitor cycle\n')
        time.sleep(10)
    return
