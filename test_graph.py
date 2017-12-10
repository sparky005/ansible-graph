import pytest
from graph import *
from graphviz import Digraph
from pyfakefs.fake_filesystem_unittest import Patcher

def test_find_nodes(roles_path, fake_nodes):
    nodes = find_nodes(roles_path)
    assert roles_path == '/tmp/playbooks'
    assert isinstance(nodes, list)
    assert len(nodes) == 6
    assert isinstance(nodes[0], str)
    assert all('yml' in node or 'yaml' in node for node in nodes)

def test_parse_playbooks(playbooks, fake_nodes):
    edges = parse_playbooks(playbooks)
    assert isinstance(edges, list)
    assert len(edges) == 3
    assert isinstance(edges[0], tuple)

def test_parse_roles(roles, fake_nodes):
    edges = parse_roles(roles)
    assert isinstance(edges, list)
    assert len(edges) == 3
    assert isinstance(edges[0], tuple)
    assert all('roles' in edge[0] for edge in edges)

def test_parse_roles_and_playbooks(nodes, fake_nodes):
    edges = parse_roles_and_playbooks(nodes)
    assert isinstance(edges, list)
    assert len(edges) == 6
    assert isinstance(edges[0], tuple)
    assert all('yml' in edge[0] or 'yaml' in edge[0] or
                'yml' in edge[1] or 'yaml' in edge[1] for edge in edges)

def test_rename_edges(raw_edges, roles, fake_nodes):
    edges = rename_edges(raw_edges, roles)
    assert isinstance(edges, list)
    assert len(edges) == 6
    assert isinstance(edges[0], tuple)
    assert all('yml' in edge[0] or 'yaml' in edge[0] for edge in edges)
    assert all('yml' in edge[1] or 'yaml' in edge[1] for edge in edges)

def test_build_graph(named_edges):
    graph = build_graph(named_edges)
    assert isinstance(graph, Digraph)
    source = graph.source
    assert "Ansible Dependency Tree" in source
    assert all(edge[0] in source and edge[1] in source for edge in named_edges)
