from tests import venv_path, clone_path, TestBase, tmplocation
import os
import clonevirtualenv
import sys
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
        assert link == os.path.join(tmplocation, 'symlink')
        assert os.readlink(link) == 'new_location'

    def test_fixup_rel_link(self):
        link = os.path.relpath(os.path.join(tmplocation, 'symlink'))
        assert not os.path.isabs(link),\
                'Expected relative path link for test'

        os.symlink('original_location', link)
        assert os.readlink(link) == 'original_location'

        clonevirtualenv._replace_symlink(link, 'new_location')
        assert link == os.path.relpath(os.path.join(tmplocation, 'symlink'))
        assert os.readlink(link) == 'new_location'

    def test_fixup_script_(self):

        script = '''#!%s/bin/python
# EASY-INSTALL-ENTRY-SCRIPT: 'console_scripts'
import sys

if __name__ == '__main__':
    print('Testing VirtualEnv-Clone!')
    sys.exit()''' % venv_path

        # want to do this manually,
        # so going to call clone before the file exists
        # run virtualenv-clone
        sys.argv = ['virtualenv-clone', venv_path, clone_path]
        clonevirtualenv.main()

        root = os.path.join(clone_path, 'bin')
        new_ = os.path.join(clone_path, 'bin', 'clonetest')
        # write the file straight to the cloned
        with open(new_, 'w') as f:
            f.write(script)

        # run fixup
        clonevirtualenv.fixup_script_(root,
            'clonetest', venv_path, clone_path, '2.7')

        with open(new_, 'r') as f:
            data = f.read()

        assert venv_path not in data
        assert clone_path in data

    def test_fixup_script_no_shebang(self):
        '''Verify if there is no shebang nothing is altered'''

        script = '''%s/bin/python
# EASY-INSTALL-ENTRY-SCRIPT: 'console_scripts'
import sys

if __name__ == '__main__':
    print('Testing VirtualEnv-Clone!')
    sys.exit()''' % venv_path

        # want to do this manually,
        # so going to call clone before the file exists
        # run virtualenv-clone
        sys.argv = ['virtualenv-clone', venv_path, clone_path]
        clonevirtualenv.main()

        root = os.path.join(clone_path, 'bin')
        new_ = os.path.join(clone_path, 'bin', 'clonetest')
        # write the file straight to the cloned
        with open(new_, 'w') as f:
            f.write(script)

        # run fixup
        clonevirtualenv.fixup_script_(root,
            'clonetest', venv_path, clone_path, '2.7')

        with open(new_, 'r') as f:
            data = f.read()

        assert venv_path in data
        assert clone_path not in data
        assert clone_path + '/bin/python2.7' not in data

    def test_fixup_script_version(self):
        '''Verify if version is updated'''

        script = '''#!%s/bin/python2.7
# EASY-INSTALL-ENTRY-SCRIPT: 'console_scripts'
import sys

if __name__ == '__main__':
    print('Testing VirtualEnv-Clone!')
    sys.exit()''' % venv_path

        # want to do this manually,
        # so going to call clone before the file exists
        # run virtualenv-clone
        sys.argv = ['virtualenv-clone', venv_path, clone_path]
        clonevirtualenv.main()

        root = os.path.join(clone_path, 'bin')
        new_ = os.path.join(clone_path, 'bin', 'clonetest')
        # write the file straight to the cloned
        with open(new_, 'w') as f:
            f.write(script)

        # run fixup
        clonevirtualenv.fixup_script_(root,
            'clonetest', venv_path, clone_path, '2.7')

        with open(new_, 'r') as f:
            data = f.read()

        assert venv_path not in data
        assert clone_path in data

        assert clone_path + '/bin/python2.7' in data
