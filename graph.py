#!/usr/bin/env python

import os
import argparse
import glob
import logging
import yaml
from graphviz import Digraph
# pylint: disable=invalid-name
# pylint: disable=line-too-long

# set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('ansible-graph.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

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
    # we don't care about the following types of files
    # so we will exclude them from the list of nodes
    # they will never be dependents, only dependencies
    exclusions = 'templates', 'vars', 'defaults', 'handlers', 'meta', 'shared'
    return [f for f in glob.iglob(os.path.join(roles_path, '**/*.y*ml'), recursive=True) if not any(x in f for x in exclusions)]

def parse_playbook(node):
    """Parses a single playbook"""
    edges = []
    logger.info("Now processing %s", node)
    try:
        with open(node, 'r') as f:
            playbook = yaml.load(f)
    except yaml.constructor.ConstructorError:
        logger.error("Could not parse %s. This can happen with files that have a vault key. Skipping", node)
        return None
    # playbook gets loaded as a len 1 list of dicts
    # set y = 1 element, to make life easier
    playbook = playbook[0]

    # handle empty file
    if not playbook:
        return None

    # yaml file is broken down by header
    # first, we just get the listed roles in roles:
    try:
        for role in playbook['roles']:
            # roles that have variables are dicts
            if isinstance(role, dict):
                edges.append((node, role['role']))
            else:
                edges.append((node, role))
    except KeyError:
        logger.warning("No roles found in %s", node)

    # next, we get the roles that are called by include_role
    # these are in the task key
    try:
        for task in playbook['tasks']:
            for key, value in task.items():
                if key == 'include_role':
                    edges.append((node, value['name']))
    except KeyError:
        logger.warning("No tasks found in %s", node)
    except TypeError:
        logger.warning("Could not parse part of %s. Likely malformed file.", node)
    return edges

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
        roles = find_nodes(roles_path)
        for role in roles:
            print(role)
