import os
import shutil
import subprocess
import tempfile
from unittest import TestCase

# Global test variables
tmplocation = tempfile.mkdtemp()
venv_path = os.path.realpath(os.path.join(tmplocation,'srs_venv'))
clone_path = os.path.realpath(os.path.join(tmplocation,'clone_venv'))
versions = ['2.7', '3.4', '3.5', '3.6', '3.7', '3.8']

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
