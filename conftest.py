import pytest
from pyfakefs.fake_filesystem_unittest import Patcher

@pytest.fixture
def roles_path():
    return '/tmp/playbooks'

@pytest.fixture
def playbooks():
    return ['/tmp/playbooks/test_playbook.yml', '/tmp/playbooks/test2.yml']

@pytest.fixture
def roles():
    return []

@pytest.yield_fixture(scope='session')
def fake_nodes():
    """ Fake filesystem. """
    patcher = Patcher()
    patcher.setUp()
    # TODO: create some linux playbooks in subdir
    # for more realistic test
    patcher.fs.CreateFile('/tmp/playbooks/test_playbook.yml',
                        contents="""---
                        - hosts: all
                          gather_facts: true
                          ignore_errors: true
                        
                          roles:
                            - windows_common
                            - { role: dept_common, app_version: 2 }
                          tasks:
                            - include_role:
                                name: application/application2
                        """)
    patcher.fs.CreateFile('/tmp/playbooks/test2.yml',
                        contents="""---
                        - hosts: all
                          tasks:
                          """)
    yield
    patcher.tearDown()

