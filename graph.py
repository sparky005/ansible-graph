#!/usr/bin/env python

import os
import argparse
import yaml
import glob
from graphviz import Digraph
# pylint: disable=invalid-name
roles_base = './roles'

# i think here we should just return src, dest tuples
# instead of a list of roles
def parse_single_file(file):
    """Parses a single playbook"""
    roles = []
    with open(file, 'r') as f:
        playbook = yaml.load(f)
    # yaml gets loaded as a len 1 list of dicts
    # set y = 1 element, to make life easier
    playbook = playbook[0]

    # yaml file is broken down by header
    # first, we just get the listed roles in roles:
    for role in playbook['roles']:
        # roles that have variables are dicts
        if isinstance(role, dict):
            roles.append(role['role'])
        else:
            roles.append(role)

    # next, we get the roles that are called by include_role
    # these are in the task key
    for task in playbook['tasks']:
        for key, value in task.items():
            if key == 'include_role':
                roles.append(value['name'])

    return roles

# maybe instead i should just glob the whole directory structure
# and create a link whenever i find hte word 'include'
def link_roles(dependent, depended):
    """
    Links the roles we've found
    Dependent should be a role path
    depended should be a list of roles on which
    depended depends
    """
    dot = Digraph(comment='The Round Table')
    dot.attr(size='18,50', layout='dot')
    dot.graph_attr['rankdir'] = 'LR'
    # create main node
    dot.node('head', dependent)
    for role in depended:
        dot.edge('head', role)
    dot.render('test-output/round-table.gv', view=True)
    print(dot.source)

def find_nodes(roles_path):
    for filename in glob.iglob(os.path.join(roles_path, '**/*.y*ml'), recursive=True):
        print(filename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--file',
        '-f',
        help='File to generate graph',
    )
    parser.add_argument(
        '--roles-path',
        '-r',
        help='Path to roles directory'
    )
    args = parser.parse_args()

    if args.file:
        role_path = args.file
        roles = parse_single_file(role_path)
        link_roles(role_path, roles)
    else:
        roles_path = args.roles_path
        find_nodes(roles_path)
