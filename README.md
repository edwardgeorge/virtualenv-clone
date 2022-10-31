virtualenv cloning script.


[![Build Status](https://travis-ci.org/edwardgeorge/virtualenv-clone.svg?branch=master)](https://travis-ci.org/edwardgeorge/virtualenv-clone)

A script for cloning a non-relocatable virtualenv.


```

python -m clonevirtualenv /path/to/ /path/to/venv

```

Virtualenv provides a way to make virtualenv's relocatable which could then be
copied as we wanted. However making a virtualenv relocatable this way breaks
the no-site-packages isolation of the virtualenv as well as other aspects that
come with relative paths and `/usr/bin/env` shebangs that may be undesirable.

Also, the .pth and .egg-link rewriting doesn't seem to work as intended. This
attempts to overcome these issues and provide a way to easily clone an
existing virtualenv.

It performs the following:

- copies `sys.argv[1]` dir to `sys.argv[2]`
- updates the hardcoded `VIRTUAL_ENV` variable in the activate script to the
  new repo location. (`--relocatable` doesn't touch this)
- updates the shebangs of the various scripts in bin to the new Python if
  they pointed to the old Python. (version numbering is retained.)

    it can also change `/usr/bin/env python` shebangs to be absolute too,
    though this functionality is not exposed at present.

- checks `sys.path` of the cloned virtualenv and if any of the paths are from
  the old environment it finds any `.pth` or `.egg` link files within sys.path
  located in the new environment and makes sure any absolute paths to the
  old environment are updated to the new environment.

- finally it double checks `sys.path` again and will fail if there are still
  paths from the old environment present.

This script clones virtual enviroments, it does not clone your python installation into a virtual environment. 

NOTE: This script requires Python 2.7 or 3.4+
