import requests
from urllib.parse import urljoin

ETHERMINE_API_HOST = 'https://api.ethermine.org'
ETHERMINE_HISTORY_API = 'miner/{wallet}/history'
ETHERMINE_STATISTICS_API = 'miner/{wallet}/currentStats'

WALLET = ''

worker_name = 'default'


def to_metric_name(*name):
    return '.'.join(['etheermine', worker_name] + list(name))


counters = {}
def to_counter(name, value):
    value = int(value)
    previous_value = counters.get(name, value)

    if previous_value > value:
        previous_value = 0

    diff = value - previous_value
    counters[name] = value
    return diff


def get_metrics_data():
    statistics = requests.get(urljoin(ETHERMINE_API_HOST, ETHERMINE_STATISTICS_API).format(wallet=WALLET)).json()['data']

    metrics = [
        {
            'metric': to_metric_name('current_hashrate'),
            'points': statistics['currentHashrate'],
            'type': 'gauge',
        },
        {
            'metric': to_metric_name('average_hashrate'),
            'points': statistics['averageHashrate'],
            'type': 'gauge',
        },
        {
            'metric': to_metric_name('valid_shares'),
            'points': statistics['validShares'],
            'type': 'gauge',
        },
        {
            'metric': to_metric_name('stale_shares'),
            'points': statistics['staleShares'],
            'type': 'gauge',
        },
        {
            'metric': to_metric_name('unpaid'),
            'points': statistics['unpaid'] / 1000000000000000000.,
            'type': 'gauge',
        },
        {
            'metric': to_metric_name('coins_per_min'),
            'points': statistics['coinsPerMin'],
            'type': 'gauge',
        },
        {
            'metric': to_metric_name('usd_per_min'),
            'points': statistics['usdPerMin'],
            'type': 'gauge',
        },
    ]

    return metrics
