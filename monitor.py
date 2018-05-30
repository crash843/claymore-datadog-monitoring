import time
import datetime

import datadog

import miner
from ext import netatmo


refresh_time = 5

DATADOG_API_KEY = ''

datadog.initialize(api_key=DATADOG_API_KEY)


if __name__ == '__main__':
    while True:
        metrics = []
        try:
            metrics.extend(miner.get_metrics_data())
        except Exception as e:
            print(e)

        try:
            metrics.extend(netatmo.get_metrics_data())
        except Exception as e:
            print(e)

        try:
            print(metrics)
            datadog.api.Metric.send(metrics)
            print('datadog metrics sent %s' % datetime.datetime.now())
            print('-' * 30)
        except Exception as e:
            print(e)
        finally:
            time.sleep(refresh_time)
