import os
import shutil
import py
import subprocess
from unittest import TestCase

# Global test variables
tmplocation = py.path.local.mkdtemp().strpath
venv_path = os.path.join(tmplocation,'srs_venv')
clone_path = os.path.join(tmplocation,'clone_venv')
versions = ['2.6','2.7','3.2']

def clean():
    if os.path.exists(tmplocation): shutil.rmtree(tmplocation)


class TestBase(TestCase):

    def setUp(self):
        """Clean from previous testing"""
        clean()

        """Create a virtualenv to clone"""
        assert subprocess.call(['virtualenv', venv_path]) == 0,\
             "Error running virtualenv"

        # verify starting point...
        assert os.path.exists(venv_path), 'Virtualenv to clone does not exists'

    def tearDown(self):
        """Clean up our testing"""
        clean()
