from tests import venv_path, clone_path, TestBase, tmplocation
import os
import clonevirtualenv
import sys
import time
import stat

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

    def test_fixup_script_different_version(self):
        '''Verify if version is updated'''

        script = '''#!%s/bin/python2
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

        assert clone_path + '/bin/python2' in data

    def test_fixup_pth_file(self):
        '''Prior to version 0.2.7, the method fixup_pth_file() wrongly wrote unicode files'''

        content = os.linesep.join(('/usr/local/bin/someFile', '/tmp/xyzzy', '/usr/local/someOtherFile', ''))
        pth = '/tmp/test_fixup_pth_file.pth'

        with open(pth, 'w') as fd:
            fd.write(content)

        # Find size of file - should be plain ASCII/UTF-8...

        org_stat = os.stat(pth)
        assert len(content) == org_stat[stat.ST_SIZE]

        # Now sleep for 2 seconds, then call fixup_pth_file(). This should ensure that the stat.ST_MTIME has
        # changed if the file has been changed/rewritten

        time.sleep(2)
        clonevirtualenv.fixup_pth_file(pth, '/usr/local', '/usr/xyzzy')
        new_stat = os.stat(pth)
        assert org_stat[stat.ST_MTIME] != new_stat[stat.ST_MTIME]  # File should have changed
        assert org_stat[stat.ST_SIZE] == new_stat[stat.ST_SIZE]  # Substituting local->xyzzy - size should be the same

        os.remove(pth)
