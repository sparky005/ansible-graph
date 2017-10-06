#!/usr/bin/env python

import yaml
from graphviz import Graph, Digraph

roles_base = './roles'

def parse_single_file(file):
    roles = []
    with open(file, 'r') as f:
        y = yaml.load(f)
    # yaml gets loaded as a len 1 list of dicts
    # set y = 1 element, to make life easier
    y = y[0]

    # yaml file is broken down by header
    # first, we just get the listed roles in roles:
    for role in y['roles']:
        if type(role) is dict:
            roles.append(role['role'])
        else:
            roles.append(role)

    # next, we get the roles that are called by include_role
    # these are in the task key
    for task in y['tasks']:
        for key,value in task.items():
            if key == 'include_role':
                roles.append(value['name'])

    return(roles)
    

roles = parse_single_file('qs_desktop.yml')
for role in roles:
    print(role)
