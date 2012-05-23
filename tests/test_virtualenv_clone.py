from unittest import TestCase
from pytest import raises
import subprocess
import os
import shutil
import clonevirtualenv
import sys

tmplocation = os.environ.get('TMPDIR') or os.environ.get('TMP')
venv_path = os.path.join(tmplocation,'venv')
clone_path = os.path.join(tmplocation,'clone_venv')

class TestVirtualenvClone(TestCase):

    def setUp(self):
        """Clean from previous testing"""
        if os.path.exists(venv_path): shutil.rmtree(venv_path)
        if os.path.exists(clone_path): shutil.rmtree(clone_path)

        """Create a virtualenv to clone"""
        assert subprocess.call(['virtualenv', venv_path]) == 0, "Error running virtualenv"

        # verify starting point...
        assert os.path.exists(venv_path), 'Virtualenv to clone does not exists'


    def tearDown(self):
        """Clean up our testing"""
        if os.path.exists(venv_path): shutil.rmtree(venv_path)
        if os.path.exists(clone_path): shutil.rmtree(clone_path)

    def test_clone_with_no_args(self):
        sys.argv = ['virtualenv-clone']

        with raises(SystemExit):
            clonevirtualenv.main()

    def test_clone_with_1_arg(self):
        sys.argv = ['virtualenv-clone', venv_path]

        with raises(SystemExit):
            clonevirtualenv.main()

    def test_clone_with_bad_src(self):
        sys.argv = ['virtualenv-clone', os.path.join('this','venv','does','not','exist'), clone_path]

        with raises(SystemExit):
            clonevirtualenv.main()

    def test_clone_exists(self):
        """Verify a cloned virtualenv exists"""
        # run virtualenv-clone
        sys.argv = ['virtualenv-clone', venv_path, clone_path]
        clonevirtualenv.main()

        # verify cloned venv exists at the path specified
        assert os.path.exists(clone_path), 'Cloned Virtualenv does not exists'

    def test_clone_contents(self):
        """Walk the virtualenv and verify equivalent in clonedenv"""

        sys.argv = ['virtualenv-clone', venv_path, clone_path]
        clonevirtualenv.main()

        for root, dirs, files in os.walk(venv_path):
            clone_root = root.replace(venv_path,clone_path)
            for dir_ in dirs:
                dir_in_clone = os.path.join(clone_root,dir_)
                assert os.path.exists(dir_in_clone),\
                    'Directory %s is missing from cloned virtualenv' % dir_

            for file_ in files:
                if file_.endswith('.pyc'):
                    continue
                file_in_clone = os.path.join(clone_root,file_)
                assert os.path.exists(file_in_clone),\
                    'File %s is missing from cloned virtualenv' % file_

                with open(file_in_clone, 'rb') as f:
                    lines = f.read()
                    assert venv_path not in lines, 'Found copied path in %s' % file_in_clone
