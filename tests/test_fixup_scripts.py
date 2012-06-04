from tests import venv_path, clone_path, TestBase, tmplocation
import os
import clonevirtualenv
"""
Fixup scripts meerly just walks bin dir and calls to
fixup_link, fixup_activate, fixup_script_
"""


class TestFixupScripts(TestBase):

    def test_fixup_activate(self):
        file_ = os.path.join(venv_path, 'bin', 'activate')
        with open(file_, 'rb') as f:
            data = f.read().decode('utf-8')

        # verify initial state
        assert venv_path in data
        assert clone_path not in data
        assert os.path.basename(clone_path) not in data
        clonevirtualenv.fixup_activate(file_, venv_path, clone_path)

        with open(file_, 'rb') as f:
            data = f.read().decode('utf-8')

        # verify changes
        assert venv_path not in data
        assert os.path.basename(venv_path) not in data
        assert clone_path in data

    def test_fixup_abs_link(self):
        link = os.path.join(tmplocation, 'symlink')
        assert os.path.isabs(link), 'Expected abs path link for test'

        os.symlink('original_location', link)
        assert os.readlink(link) == 'original_location'

        clonevirtualenv._replace_symlink(link, 'new_location')
        assert os.readlink(link) == 'new_location'

    def test_fixup_rel_link(self):
        link = os.path.join(tmplocation, 'symlink')
        assert not os.path.isabs(link),\
                'Expected relative path link for test'

        os.symlink('original_location', link)
        assert os.readlink(link) == 'original_location'

        clonevirtualenv._replace_symlink(link, 'new_location')
        assert os.readlink(link) == 'new_location'

    def test_replace_symlink(self):
        pass

    def test_fixup_script_(self):
        pass
