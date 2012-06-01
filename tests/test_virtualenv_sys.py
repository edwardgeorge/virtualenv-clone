import os
import subprocess
from unittest import TestCase
import clonevirtualenv
import sys
from tests import venv_path, clone_path, versions, clean

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

            venv_version = clonevirtualenv._virtualenv_sys(venv_path)[0]
            assert version == venv_version, 'Expected version %s' % version

            # clean so next venv can be made
            clean()

    def test_virtualenv_syspath(self):
        """Verify syspath for created virtualenvs"""
        for version in versions:
            # create a virtualenv
            assert subprocess.call(['virtualenv', '-p', 'python' + version,
                    venv_path]) == 0, "Error running virtualenv"

            sys_path = clonevirtualenv._virtualenv_sys(venv_path)[1]

            paths = [path for path in sys_path]
            assert paths, "There should be path information"

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

            clone_version = clonevirtualenv._virtualenv_sys(clone_path)[0]
            assert version == clone_version, 'Expected version %s' % version

            # clean so next venv can be made
            clean()

    def test_clone_syspath(self):
        """
        Verify syspath for cloned virtualenvs

        This really is a test for fixup_syspath as well
        """
        for version in versions:
            # create a virtualenv
            assert subprocess.call(['virtualenv', '-p', 'python' + version,
                    venv_path]) == 0, "Error running virtualenv"

            # run virtualenv-clone
            sys.argv = ['virtualenv-clone', venv_path, clone_path]
            clonevirtualenv.main()

            sys_path = clonevirtualenv._virtualenv_sys(clone_path)[1]

            paths = [path for path in sys_path]
            assert paths, "There should be path information"

            assert venv_path not in paths,\
                "There is reference to the source virtualenv"

            for path in paths:
                assert os.path.basename(venv_path) not in path,\
                    "There is reference to the source virtualenv:\n%s" % path

            # clean so next venv can be made
            clean()
