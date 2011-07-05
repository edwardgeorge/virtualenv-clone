import sys

from setuptools import setup

if __name__ == '__main__' and sys.version_info < (2, 5):
    raise SystemExit("Python >= 2.5 required for virtualenv-clone")


setup(name="virtualenv-clone",
    version='0.2.2',
    description='script to clone virtualenvs.',
    author='Edward George',
    author_email='edwardgeorge@gmail.com',
    url='http://github.com/edwardgeorge/virtualenv-clone',
    py_modules=["clonevirtualenv"],
    entry_points = {
        'console_scripts': [
            'virtualenv-clone=clonevirtualenv:main',
    ]},
    classifiers = [
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
    ], )
