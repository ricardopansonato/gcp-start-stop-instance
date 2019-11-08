#!/usr/bin/env python3

import logging
import os
import yaml
import json

from queue import Queue
from threading import Thread, Event
from datetime import datetime
from datetimerange import DateTimeRange

from googleapiclient import discovery
from google.oauth2 import service_account
from oauth2client.client import GoogleCredentials

from argparse import ArgumentParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobUtility(object):
    @staticmethod
    def convert_active_ranges(active_hours):
        active_ranges = []
        for hours in active_hours.split(","):
            values = hours.split('-')
            begin = datetime.now().replace(hour=int(values[0]), minute=0, second=0, microsecond=0)
            end = datetime.now().replace(hour=int(values[1])-1, minute=59, second=59, microsecond=999)
            active_ranges.append(DateTimeRange(begin, end))
        return active_ranges
    
    @staticmethod
    def authenticate_google(key):
        with open(key, "r") as data_file:
            info = json.loads(data_file.read())
        credentials = service_account.Credentials.from_service_account_info(info)
        return discovery.build('compute', 'v1', credentials=credentials, cache_discovery=False)
    
    @staticmethod
    def is_active_hour(active_hours):
        active_ranges = JobUtility.convert_active_ranges(active_hours)
        current_datetime = datetime.now()
        is_active_hour = False
        for active_range in active_ranges:
            is_active_hour = current_datetime in active_range
            if is_active_hour:
                 break;
        return is_active_hour
    
class StartStopWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            project, key, zone, instance, scheduler = self.queue.get()
            info = {}
            try:
                week_day = scheduler['week_day'].split(",")
                current_week_day = datetime.now().strftime('%a')
                service = JobUtility.authenticate_google(key) 
                is_active_hour = JobUtility.is_active_hour(scheduler['active_hours'])
                
                if current_week_day in week_day and is_active_hour:
                    request = service.instances().start(project=project, zone=zone, instance=instance)
                    response = request.execute()
                else:
                    request = service.instances().stop(project=project, zone=zone, instance=instance)
                    response = request.execute()
            except Exception as e: print(e)
            finally:
                self.queue.task_done()

def main():
    quit_event = Event()
    queue = Queue()
    
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", dest="config", help="path to config file", metavar="CONF")
    parser.add_argument("-w", "--worker", dest="worker", help="number of workers", metavar="WORK")
    
    args = parser.parse_args()
    
    for x in range(int(args.worker)):
        worker = StartStopWorker(queue)
        worker.daemon = True
        worker.start()
    
    with open(args.config) as file:
        config = yaml.full_load(file)
        for projects in config:
            for project, value in projects.items():
                for zone, instances in value['zones'].items():
                    for instance, scheduler in instances.items():
                        logger.info('Queueing {}, {}, {}, {}, {}'.format(project, value['key'], zone, instance, scheduler))
                        queue.put((project, value['key'], zone, instance, scheduler))
    
    quit_event.set()
    queue.join()

if __name__ == '__main__':
    main()
