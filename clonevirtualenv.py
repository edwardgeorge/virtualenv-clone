#!/opt/python27/bin/python
from __future__ import with_statement
import logging
import optparse
import os
import shutil
import subprocess
import sys

version_info = (0, 2, 2)
__version__ = '.'.join(map(str, version_info))


logger = logging.getLogger()
ONLY_FIXUP=False

class UserError(Exception):
    pass


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
    p = subprocess.Popen([executable,
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
    global ONLY_FIXUP
    if not os.path.exists(src_dir):
        raise UserError('src dir %r does not exist' % src_dir)
    if (not ONLY_FIXUP) and os.path.exists(dst_dir):
        raise UserError('dest dir %r exists' % dst_dir)
    #sys_path = _virtualenv_syspath(src_dir)
    if not ONLY_FIXUP:
        shutil.copytree(src_dir, dst_dir, symlinks=True)
    if ONLY_FIXUP:
        version, sys_path = _virtualenv_sys(src_dir)
    else:
        version, sys_path = _virtualenv_sys(dst_dir)
    fixup_scripts(src_dir, dst_dir, version)

    has_old = lambda s: any(i for i in s if _dirmatch(i, src_dir))

    #if has_old(sys_path):
    # only need to fix stuff in sys.path if we have old
    # paths in the sys.path of new python env. right?
    fixup_syspath_items(sys_path, src_dir, dst_dir)
    if ONLY_FIXUP:
        remaining = has_old(_virtualenv_sys(src_dir)[1])
    else:
        remaining = has_old(_virtualenv_sys(dst_dir)[1])
        assert not remaining, _virtualenv_sys(dst_dir)


def fixup_scripts(old_dir, new_dir, version, rewrite_env_python=False):
    if ONLY_FIXUP:
        bin_dir = os.path.join(old_dir, 'bin')
    else:
        bin_dir = os.path.join(new_dir, 'bin')
    root, dirs, files = os.walk(bin_dir).next()
    for file_ in files:
        filename = os.path.join(root, file_)
        if file_ == 'activate':
            fixup_activate(os.path.join(root, file_), old_dir, new_dir)
        elif file_ in ['python', 'python%s' % version, 'activate_this.py']:
            continue
        elif os.path.islink(filename):
            fixup_link(filename, old_dir, new_dir)
        elif os.path.isfile(filename):
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

    origdir = os.path.dirname(os.path.abspath(filename)).replace(
        new_dir, old_dir)
    if not os.path.isabs(target):
        target = os.path.abspath(os.path.join(origdir, target))
        rellink = True
    else:
        rellink = False

    if _dirmatch(target, old_dir):
        if rellink:
            # keep relative links, but don't keep original in case it
            # traversed up out of, then back into the venv.
            # so, recreate a relative link from absolute.
            target = target[len(origdir):].lstrip(os.sep)
        else:
            target = target.replace(old_dir, new_dir, 1)

    # else: links outside the venv, replaced with absolute path to target.
    _replace_symlink(filename, target)


def _replace_symlink(filename, newtarget):
    tmpfn = "%s.new" % filename
    os.symlink(newtarget, tmpfn)
    os.rename(tmpfn, filename)


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


def main():
    global ONLY_FIXUP
    parser = optparse.OptionParser("usage: %prog --source /path/to/existing/venv"
        " --dest /path/to/cloned/venv [--fixup] ")
    parser.add_option("--fixup", dest="fixup", default=False, action="store_true",
                        help=("Do not copy files, only fixup the files in the "
                              "given source env to point to the new destination"))
    parser.add_option("--source", dest="source", default="")
    parser.add_option("--dest", dest="dest", default="")
    options, args = parser.parse_args()
    old_dir = options.source
    new_dir = options.dest
    if not old_dir or not new_dir:
        parser.error("not enough arguments given.")
    ONLY_FIXUP = options.fixup
    old_dir = os.path.normpath(os.path.abspath(old_dir))
    new_dir = os.path.normpath(os.path.abspath(new_dir))
    logging.basicConfig(level=logging.WARNING)
    try:
        clone_virtualenv(old_dir, new_dir)
    except UserError, e:
        parser.error(str(e))


if __name__ == '__main__':
    main()
