import pytest
from graph import *

def test_find_nodes(roles_path):
    nodes = find_nodes(roles_path)
    assert roles_path == './roles'
    assert isinstance(nodes, list)
