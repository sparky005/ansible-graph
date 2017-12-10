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
    return ['/tmp/playbooks/roles/windows_common/tasks/main.yml',
            '/tmp/playbooks/roles/dept_common/tasks/main.yml',
            '/tmp/playbooks/roles/application/application2/tasks/main.yml']

@pytest.yield_fixture(scope='session')
def fake_nodes():
    """ Fake filesystem. """
    patcher = Patcher()
    patcher.setUp()
    # TODO: create some linux playbooks in subdir
    # for more realistic test

    # fake playbooks
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

    # fake roles
    patcher.fs.CreateFile('/tmp/playbooks/roles/windows_common/tasks/main.yml',
                        contents="""---
                        - include_role:
                            name: applications/test_inclusion
                        """)
    patcher.fs.CreateFile('/tmp/playbooks/roles/dept_common/tasks/main.yml',
                        contents="""---
                        - include_role:
                            name: applications/test_inclusion
                        """)
    patcher.fs.CreateFile('/tmp/playbooks/roles/application/application2/tasks/main.yml',
                        contents="""---
                        - include_role:
                            name: applications/test_inclusion
                        """)
    patcher.fs.CreateFile('/tmp/playbooks/roles/applications/test_inclusion/tasks/main.yml',
                        contents="""---
                        - name: say hi
                          win_ping
                            data: hi
                        """)
    yield
    patcher.tearDown()

