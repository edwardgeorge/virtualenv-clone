import os
import subprocess
from unittest import TestCase
import clonevirtualenv
import sys
from tests import tmplocation, venv_path, clone_path, versions, clean

class TestVirtualenvSys(TestCase):

    def setUp(self):
        """Clean from previous testing"""
        clean()

    def tearDown(self):
        """Clean up our testing"""
        clean()

    def test_virtualenv_versions(self):
        """Verify version for created virtualenvs"""
        for version in versions:
            # create a virtualenv
            assert subprocess.call(['virtualenv', '-p', 'python' + version,
                    venv_path]) == 0, "Error running virtualenv"

            venv_version, sys_path = clonevirtualenv._virtualenv_sys(venv_path)
            assert version == venv_version, 'Expected version %s' % version

            # clean so next venv can be made
            clean()

    def test_clone_version(self):
        """Verify version for cloned virtualenvs"""
        for version in versions:
            # create a virtualenv
            assert subprocess.call(['virtualenv', '-p', 'python' + version,
                    venv_path]) == 0, "Error running virtualenv"

            # run virtualenv-clone
            sys.argv = ['virtualenv-clone', venv_path, clone_path]
            clonevirtualenv.main()

            clone_version, sys_path = clonevirtualenv._virtualenv_sys(clone_path)
            assert version == clone_version, 'Expected version %s' % version

            # clean so next venv can be made
            clean()
