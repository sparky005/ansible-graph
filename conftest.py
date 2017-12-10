import pytest
from pyfakefs.fake_filesystem_unittest import Patcher

@pytest.fixture
def roles_path():
    return '/tmp/playbooks'

@pytest.fixture
def playbooks():
    return ['/tmp/playbooks/windows/test_playbook.yml', '/tmp/playbooks/windows/test2.yml']

@pytest.fixture
def roles():
    return ['/tmp/playbooks/windows/roles/windows_common/tasks/main.yml',
            '/tmp/playbooks/windows/roles/dept_common/tasks/main.yml',
            '/tmp/playbooks/windows/roles/application/application2/tasks/main.yml',
            '/tmp/playbooks/windows/roles/applications/test_inclusion/tasks/main.yml']

@pytest.fixture
def nodes(roles, playbooks):
    return roles + playbooks

@pytest.fixture
def edges():
    return [('/tmp/playbooks/windows/test_playbook.yml', 'windows_common'),
            ('/tmp/playbooks/windows/test_playbook.yml', 'dept_common'),
            ('/tmp/playbooks/windows/test_playbook.yml', 'application/application2'),
            ('/tmp/playbooks/windows/roles/windows_common/tasks/main.yml', 'applications/test_inclusion'),
            ('/tmp/playbooks/windows/roles/dept_common/tasks/main.yml', 'applications/test_inclusion'),
            ('/tmp/playbooks/windows/roles/application/application2/tasks/main.yml', 'applications/test_inclusion')]

@pytest.yield_fixture(scope='session')
def fake_nodes():
    """ Fake filesystem. """
    patcher = Patcher()
    patcher.setUp()
    # TODO: create some linux playbooks in subdir
    # for more realistic test

    # fake playbooks
    patcher.fs.CreateFile('/tmp/playbooks/windows/test_playbook.yml',
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
    patcher.fs.CreateFile('/tmp/playbooks/windows/test2.yml',
                        contents="""---
                        - hosts: all
                          tasks:
                          """)

    # fake roles
    patcher.fs.CreateFile('/tmp/playbooks/windows/roles/windows_common/tasks/main.yml',
                        contents="""---
                        - include_role:
                            name: applications/test_inclusion
                        """)
    patcher.fs.CreateFile('/tmp/playbooks/windows/roles/dept_common/tasks/main.yml',
                        contents="""---
                        - include_role:
                            name: applications/test_inclusion
                        """)
    patcher.fs.CreateFile('/tmp/playbooks/windows/roles/application/application2/tasks/main.yml',
                        contents="""---
                        - include_role:
                            name: applications/test_inclusion
                        """)
    patcher.fs.CreateFile('/tmp/playbooks/windows/roles/applications/test_inclusion/tasks/main.yml',
                        contents="""---
                        - name: say hi
                          win_ping:
                            data: hi
                        """)
    yield
    patcher.tearDown()

