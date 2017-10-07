#!/usr/bin/env python

import yaml
from graphviz import Digraph

roles_base = './roles'

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

def link_roles(dependent, depended):
    """
    Links the roles we've found
    Dependent should be a role path
    depended should be a list of roles on which
    depended depends
    """
    dot = Digraph(comment='The Round Table')
    dot.attr(size='18,50', layout='dot')
    # create main node
    dot.node('head', dependent)
    for role in depended:
        dot.node(role)
        dot.edge('head', role)
    dot.render('test-output/round-table.gv', view=True)
    print(dot.source)


if __name__ == '__main__':
    role_path = '/home/asadik/repos/playbooks/windows/qs_desktop.yml'
    roles = parse_single_file(role_path)
    link_roles(role_path, roles)
