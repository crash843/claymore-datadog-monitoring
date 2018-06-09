import time
import datetime

import datadog

import miner
import ethermine
from ext import netatmo


refresh_time = 5

DATADOG_API_KEY = ''

datadog.initialize(api_key=DATADOG_API_KEY)


if __name__ == '__main__':
    netatmo_last_updated = datetime.datetime.now() - datetime.timedelta(hours=1)
    ethermine_last_updated = datetime.datetime.now() - datetime.timedelta(hours=1)

    while True:
        metrics = []
        try:
            metrics.extend(miner.get_metrics_data())
        except Exception as e:
            print(e)

        try:
            if (datetime.datetime.now() - netatmo_last_updated).seconds > 250:
                metrics.extend(netatmo.get_metrics_data())
                netatmo_last_updated = datetime.datetime.now()
        except Exception as e:
            print(e)

        try:
            if (datetime.datetime.now() - ethermine_last_updated).seconds > 250:
                metrics.extend(ethermine.get_metrics_data())
                ethermine_last_updated = datetime.datetime.now()
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
