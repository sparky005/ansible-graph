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

def find_nodes(roles_path):
    # we don't care about the following types of files
    # so we will exclude them from the list of nodes
    # they will never be dependents, only dependencies
    exclusions = 'templates', 'vars', 'defaults', 'handlers', 'meta', 'shared'
    return [f for f in glob.iglob(os.path.join(roles_path, '**/*.y*ml'), recursive=True) if not any(x in f for x in exclusions)]


def parse_role(node, task):
    edges = []
    try:
        for key, value in task.items():
            if key == 'include' or key == 'include_role':
                if isinstance(value, dict):
                    # roles that have variables are dicts
                    edges.append((node, value['name']))
                else:
                    # otherwise, they're just strings
                    edges.append((node, value))
    except AttributeError:
        logger.warning("Hit AttributeError on %s.", node)

    return edges


def parse_roles(nodes):
    """Parses a list of roles"""
    edges = []
    for node in nodes:
        logger.info("Now processing %s", node)
        with open(node, 'r') as f:
            playbook = yaml.load(f)

        for task in playbook:
            if isinstance(task, dict) and 'block' in task.keys():
                task = task['block']
                for item in task:
                    edges += parse_role(node, item)
            else:
                edges += parse_role(node, task)

    return edges


def parse_playbooks(nodes):
    """Parses a list of playbooks"""
    edges = []
    for node in nodes:
        logger.info("Now processing %s", node)
        try:
            with open(node, 'r') as f:
                playbook = yaml.load(f)
        except yaml.constructor.ConstructorError:
            logger.error("Could not parse %s. This can happen with files that have a vault key. Skipping", node)
            continue
        # playbook gets loaded as a len 1 list of dicts
        # set y = 1 element, to make life easier
        playbook = playbook[0]

        # handle empty file
        if not playbook:
            continue

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

def parse_roles_and_playbooks(nodes):
    """Parse both roles and playbooks"""
    edges = []

    # separate nodes into roles and playbooks
    playbooks = [node for node in nodes if 'roles' not in node]
    roles = [node for node in nodes if 'roles' in node]

    logger.info("BEGIN PROCESSING PLAYBOOKS")
    edges = parse_playbooks(playbooks)
    logger.info("END PROCESSING PLAYBOOKS")
    logger.info("BEGIN PROCESSING ROLES")
    edges += parse_roles(roles)
    logger.info("END PROCESSING ROLES")

    return edges

def rename_edges(edges, nodes):

    # get role names
    roles = [node for node in nodes if 'roles' in node]
    # fix edge destinations to full paths
    # that match the paths we have in roles
    for i, edge in enumerate(edges):
        for role in roles:
            # get edge[0] platform
            edge_list = edge[0].split('/')
            platform = edge_list[edge_list.index('playbooks')+1]
            # rename role inclusions to point to the main.yml
            if edge[1] in role and 'main.yml' in role and platform in role:
                logger.info("Main role file found for %s", edge[1])
                logger.warning("Renaming %s to %s", edge[1], role)
                t = (edges[i][0], role)
                edges[i] = t
                break
            # rename other inclusions to point to
            # corresponding file
            elif edge[1] in role and platform in role:
                logger.info("Task file found for %s", edge[1])
                logger.warning("Renaming %s to %s", edge[1], role)
                new_edge = (edges[i][0], role)
                edges[i] = new_edge

    return edges


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--roles-path',
        '-r',
        help='Path to roles directory'
    )
    args = parser.parse_args()

    roles_path = args.roles_path
    nodes = find_nodes(roles_path)

    logger.info("Found nodes:")
    for node in nodes:
        logger.info(node)

    edges = parse_roles_and_playbooks(nodes)
    edges = rename_edges(edges, nodes)

    # remove duplicates
    edges = set(edges)

    dot = Digraph(comment='Ansible Dependency Tree', node_attr={'fontsize': '48'})
    dot.attr(ranksep='10.2', nodesep='1.2', layout='dot')
    dot.graph_attr['rankdir'] = 'LR'
    for edge in edges:
        dot.edge(edge[0], edge[1])
    dot.render('test-output/round-table.gv', view=True)
