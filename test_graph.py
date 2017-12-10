import pytest
from graph import *

def test_find_nodes(roles_path):
    nodes = find_nodes(roles_path)
    assert roles_path == '../playbooks'
    assert isinstance(nodes, list)
    assert isinstance(nodes[0], str)
    assert all('yml' in node or 'yaml' in node for node in nodes)
