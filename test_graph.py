import pytest
from graph import *
from pyfakefs.fake_filesystem_unittest import Patcher

def test_find_nodes(roles_path, fake_nodes):
    nodes = find_nodes(roles_path)
    assert roles_path == '/tmp/playbooks'
    assert isinstance(nodes, list)
    assert len(nodes) == 2
    assert isinstance(nodes[0], str)
    assert all('yml' in node or 'yaml' in node for node in nodes)

def test_parse_playbooks(playbooks, fake_nodes):
    assert isinstance(edges, list)
    assert len(edges) == 3
    assert isinstance(edges[0], tuple)
