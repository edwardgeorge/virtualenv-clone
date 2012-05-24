import os
import shutil

# Global test variables
tmplocation = os.environ.get('TMPDIR') or os.environ.get('TMP')
venv_path = os.path.join(tmplocation,'venv')
clone_path = os.path.join(tmplocation,'clone_venv')
versions = ['2.6','2.7','3.2']

def clean():
    if os.path.exists(venv_path): shutil.rmtree(venv_path)
    if os.path.exists(clone_path): shutil.rmtree(clone_path)
