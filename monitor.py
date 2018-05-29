import json
import time
import datetime
import requests
import datadog


DATADOG_API_KEY = ''
CLAYMORE_MONITORING_HOST = 'http://127.0.0.1'
CLAYMORE_MONITORING_PORT = '3232'

worker_name = 'default'
refresh_time = 5

datadog.initialize(api_key=DATADOG_API_KEY)
counters = {}


def to_metric_name(*name):
    return '.'.join(['miner', worker_name] + list(name))


def to_hash_value(value):
    return int(value) * 1000


def to_counter(name, value):
    value = int(value)
    previous_value = counters.get(name, value)

    if previous_value > value:
        previous_value = 0

    diff = value - previous_value
    counters[name] = value
    return diff


def send_metrics_data():
    response = requests.get('%s:%s' % (CLAYMORE_MONITORING_HOST, CLAYMORE_MONITORING_PORT)).text
    summary = json.loads(response.split('\n')[1].split('<br><br>')[0])['result']

    metrics = [
        {
            'metric': to_metric_name('uptime'),
            'points': int(summary[1]) / 60.,
            'type': 'gauge',
        },
        {
            'metric': to_metric_name('hashrate.all'),
            'points': to_hash_value(summary[2].split(";")[0]),
            'type': 'gauge',
        },
        {
            'metric': to_metric_name('shares_accepted.all'),
            'points': to_counter('shares_accepted', summary[2].split(";")[1]),
            'type': 'count',
        },
        {
            'metric': to_metric_name('shares_rejected.all'),
            'points': to_counter('shares_rejected', summary[2].split(";")[1]),
            'type': 'count',
        }
    ]

    gpu_hashrates = list(map(to_hash_value, summary[3].split(";")))
    gpu_shares_acepted = list(map(int, summary[9].split(";")))
    gpu_temp = list(map(int, summary[6].split(";")[::2]))
    gpu_fans = list(map(int, summary[6].split(";")[1::2]))

    gpu_num = 0
    while gpu_num < len(gpu_hashrates):
        metrics.append({
            'metric': to_metric_name('hashrate'),
            'points': gpu_hashrates[gpu_num],
            'type': 'gauge',
            'tags': ['GPU:%s' % gpu_num],
        }),
        metrics.append({
            'metric': to_metric_name('shares_accepted'),
            'points': to_counter('.'.join((to_metric_name('shares_accepted'), str(gpu_num))), gpu_shares_acepted[gpu_num]),
            'type': 'count',
            'tags': ['GPU:%s' % gpu_num],
        }),
        metrics.append({
            'metric': to_metric_name('temp'),
            'points': gpu_temp[gpu_num],
            'type': 'gauge',
            'tags': ['GPU:%s' % gpu_num],
        }),
        metrics.append({
            'metric': to_metric_name('fan'),
            'points': gpu_fans[gpu_num],
            'type': 'gauge',
            'tags': ['GPU:%s' % gpu_num],
        }),
        gpu_num += 1

    print(metrics)
    datadog.api.Metric.send(metrics)
    print('datadog metrics sent %s' % datetime.datetime.now())
    print('-' * 30)


if __name__ == '__main__':
    while True:
        try:
            send_metrics_data()
        except Exception as e:
            print(e)
        finally:
            time.sleep(refresh_time)
