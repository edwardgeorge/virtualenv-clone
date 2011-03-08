"""virtualenv cloning script.

A script for cloning a non-relocatable virtualenv.

Virtualenv provides a way to make virtualenv's relocatable which could then be
copied as we wanted. However making a virtualenv relocatable this way breaks
the no-site-packages isolation of the virtualenv as well as other aspects that
come with relative paths and '/usr/bin/env' shebangs that may be undesirable.

Also, the .pth and .egg-link rewriting doesn't seem to work as intended. This
attempts to overcome these issues and provide a way to easily clone an
existing virtualenv.

It performs the following:

- copies sys.argv[1] dir to sys.argv[2]
- updates the hardcoded VIRTUAL_ENV variable in the activate script to the
  new repo location. (--relocatable doesn't touch this)
- updates the shebangs of the various scripts in bin to the new python if
  they pointed to the old python. (version numbering is retained.)

    it can also change '/usr/bin/env python' shebangs to be absolute too,
    though this functionality is not exposed at present.

- checks sys.path of the cloned virtualenv and if any of the paths are from
  the old environment it finds any .pth or .egg-link files within sys.path
  located in the new environment and makes sure any absolute paths to the
  old environment are updated to the new environment.

- finally it double checks sys.path again and will fail if there are still
  paths from the old environment present.

"""
from __future__ import with_statement
import logging
import os
import shutil
import subprocess
import sys

version_info = (0, 1, 1)
__version__ = '.'.join(map(str, version_info))


logger = logging.getLogger()


def _dirmatch(path, matchwith):
    """Check if path is within matchwith's tree.

    >>> _dirmatch('/home/foo/bar', '/home/foo/bar')
    True
    >>> _dirmatch('/home/foo/bar/', '/home/foo/bar')
    True
    >>> _dirmatch('/home/foo/bar/etc', '/home/foo/bar')
    True
    >>> _dirmatch('/home/foo/bar2', '/home/foo/bar')
    False
    >>> _dirmatch('/home/foo/bar2/etc', '/home/foo/bar')
    False
    """
    matchlen = len(matchwith)
    if (path.startswith(matchwith)
        and path[matchlen:matchlen+1] in [os.sep, '']):
        return True
    return False


def _virtualenv_sys(venv_path):
    "obtain version and path info from a virtualenv."
    executable = os.path.join(venv_path, 'bin', 'python')
    p = subprocess.Popen(['python',
        '-c', 'import sys;'
              'print sys.version[:3];'
              'print "\\n".join(sys.path);'],
        executable=executable,
        env={},
        stdout=subprocess.PIPE)
    stdout, err = p.communicate()
    assert not p.returncode and stdout
    lines = stdout.splitlines()
    return lines[0], filter(bool, lines[1:])


def clone_virtualenv(src_dir, dst_dir):
    if not os.path.exists(src_dir):
        raise Exception('src dir does not exist')
    if os.path.exists(dst_dir):
        raise Exception('dest dir exists')
    #sys_path = _virtualenv_syspath(src_dir)
    shutil.copytree(src_dir, dst_dir, symlinks=True)
    version, sys_path = _virtualenv_sys(dst_dir)
    fixup_scripts(src_dir, dst_dir, version)

    has_old = lambda s: any(i for i in s if _dirmatch(i, src_dir))

    if has_old(sys_path):
        # only need to fix stuff in sys.path if we have old
        # paths in the sys.path of new python env. right?
        fixup_syspath_items(sys_path, src_dir, dst_dir)
    remaining = has_old(_virtualenv_sys(dst_dir)[1])
    assert not remaining, _virtualenv_sys(dst_dir)


def fixup_scripts(old_dir, new_dir, version, rewrite_env_python=False):
    bin_dir = os.path.join(new_dir, 'bin')
    root, dirs, files = os.walk(bin_dir).next()
    for file_ in files:
        if file_ == 'activate':
            fixup_activate(os.path.join(root, file_), old_dir, new_dir)
        elif file_ in ['python', 'python%s' % version, 'activate_this.py']:
            continue
        elif os.path.islink(os.path.join(root, file_)):
            target = os.readlink(filename)
            if _dirmatch(target, old_dir):
                fixup_link(filename, old_dir, new_dir)
        elif os.path.isfile(os.path.join(root, file_)):
            fixup_script_(root, file_, old_dir, new_dir, version,
                rewrite_env_python=rewrite_env_python)


def fixup_script_(root, file_, old_dir, new_dir, version,
                  rewrite_env_python=False):
    old_shebang = '#!%s/bin/python' % os.path.normcase(os.path.abspath(old_dir))
    new_shebang = '#!%s/bin/python' % os.path.normcase(os.path.abspath(new_dir))
    env_shebang = '#!/usr/bin/env python'

    filename = os.path.join(root, file_)
    f = open(filename, 'rb')
    lines = f.readlines()
    f.close()

    if not lines:
        # warn: empty script
        return

    def rewrite_shebang(version=None):
        logger.debug('fixing %s' % filename)
        shebang = new_shebang
        if version:
            shebang = shebang + version
        with open(filename, 'wb') as f:
            f.write('%s\n' % shebang)
            f.writelines(lines[1:])

    bang = lines[0].strip()

    if not bang.startswith('#!'):
        return
    elif bang == old_shebang:
        rewrite_shebang()
    elif (bang.startswith(old_shebang)
          and bang[len(old_shebang):] == version):
        rewrite_shebang(version)
    elif rewrite_env_python and bang.startswith(env_shebang):
        if bang == env_shebang:
            rewrite_shebang()
        elif bang[len(env_shebang):] == version:
            rewrite_shebang(version)
    else:
        # can't do anything
        return


def fixup_activate(filename, old_dir, new_dir):
    logger.debug('fixing %s' % filename)
    f = open(filename, 'rb')
    data = f.read()
    f.close()
    data = data.replace(old_dir, new_dir)
    f = open(filename, 'wb')
    f.write(data)
    f.close()


def fixup_link(filename, old_dir, new_dir, target=None):
    logger.debug('fixing %s' % filename)
    if target is None:
        target = os.readlink(filename)
    raise NotImplementedError()


def fixup_syspath_items(syspath, old_dir, new_dir):
    for path in syspath:
        if not os.path.isdir(path):
            continue
        path = os.path.normcase(os.path.abspath(path))
        if _dirmatch(path, old_dir):
            path = path.replace(old_dir, new_dir, 1)
            if not os.path.exists(path):
                continue
        elif not _dirmatch(path, new_dir):
            continue
        root, dirs, files = os.walk(path).next()
        for file_ in files:
            filename = os.path.join(root, file_)
            if filename.endswith('.pth'):
                fixup_pth_file(filename, old_dir, new_dir)
            elif filename.endswith('.egg-link'):
                fixup_egglink_file(filename, old_dir, new_dir)


def fixup_pth_file(filename, old_dir, new_dir):
    logger.debug('fixing %s' % filename)
    with open(filename, 'rb') as f:
        lines = f.readlines()
    has_change = False
    for num, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('import '):
            continue
        elif _dirmatch(line, old_dir):
            lines[num] = line.replace(old_dir, new_dir, 1)
            has_change = True
    if has_change:
        with open(filename, 'wb') as f:
            f.writelines(lines)


def fixup_egglink_file(filename, old_dir, new_dir):
    logger.debug('fixing %s' % filename)
    with open(filename, 'rb') as f:
        link = f.read().strip()
    if _dirmatch(link, old_dir):
        link = link.replace(old_dir, new_dir, 1)
        with open(filename, 'wb') as f:
            f.write('%s\n' % link)


if __name__ == '__main__':
    old_dir, new_dir = sys.argv[1:]
    old_dir = os.path.normpath(os.path.abspath(old_dir))
    new_dir = os.path.normpath(os.path.abspath(new_dir))
    logging.basicConfig(level=logging.WARNING)
    clone_virtualenv(old_dir, new_dir)
