#!/usr/bin/env python3

import os
import sys
import yaml

from argparse import ArgumentParser

HOME_PATH=os.path.dirname(sys.argv[0])

parser = ArgumentParser()
parser.add_argument("-c", "--config", required=True, dest="config", help="path to config file", metavar="CONF")
parser.add_argument("-p", "--project", required=True, dest="project", help="path to config file", metavar="PROJ")
parser.add_argument("-k", "--key", required=True, dest="key", help="google account key", metavar="KEY")
parser.add_argument("-z", "--zone", required=True, dest="zone", help="zone", metavar="ZONE")
parser.add_argument("-i", "--instance", required=True, dest="instance", help="instance name", metavar="INST")
parser.add_argument("-a", "--active-hours", default="00-24", dest="active_hours", help="Hours that instance will be in running", metavar="ACT")
parser.add_argument("-w", "--week-days", default="Mon,Tue,Wed,Thu,Fri,Sat,Sun", dest="week_days", help="Week days that instance will be in running", metavar="WEEK")

args = parser.parse_args()

if os.path.exists("{0}/{1}".format(HOME_PATH, args.config)):
    config_file = "{0}/{1}".format(HOME_PATH, args.config)
elif os.path.exists(args.config):
    config_file = args.config
else:
    config_file = "{0}/{1}".format(HOME_PATH, args.config)
    if not os.path.isdir(os.path.dirname("{0}/{1}".format(HOME_PATH, args.config))):
        os.makedirs(os.path.dirname("{0}/{1}".format(HOME_PATH, args.config)))
    open("{0}/{1}".format(HOME_PATH, args.config),"w+").close()

if os.stat(config_file).st_size > 0:
    with open(config_file) as file:
        config = yaml.full_load(file)
else:
    config = []

if not config:
    project = { args.project: { 'key': args.key, 'zones': { args.zone: { args.instance: { 'active_hours': args.active_hours, 'week_day': args.week_days } } } } }
    config.append(project)
else:
    project_found = False
    for projects in config:
        for project, value in projects.items():
            if args.project == project:
                project_found = True
                zone_found = False
                value['key'] = args.key
                for zone, instances in value['zones'].items():
                    if args.zone == zone:
                        zone_found = True
                        instance_found = False
                        for instance, scheduler in instances.items():
                            if args.instance == instance:
                                instance_found = True
                                scheduler['active_hours'] = args.active_hours
                                scheduler['week_day'] = args.week_days
                        if not instance_found:
                            instances[args.instance] = { 'active_hours': args.active_hours, 'week_day': args.week_days }
                if not zone_found:
                    value['zones'][args.zone][args.instance] = { 'active_hours': args.active_hours, 'week_day': args.week_days }
    if not project_found:
        project = { args.project: { 'key': args.key, 'zones': { args.zone: { args.instance: { 'active_hours': args.active_hours, 'week_day': args.week_days } } } } }
        config.append(project)

with open(config_file, 'w') as yaml_file:
    yaml.dump(config, yaml_file, default_flow_style=False)
