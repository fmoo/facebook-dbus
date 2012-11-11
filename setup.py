from setuptools import setup, find_packages
from distutils.spawn import find_executable
import os.path
import imp
import pandoc.core

def require_binary(name):
    path = find_executable(name)
    assert path is not None, \
        "'%s' is a required binary for building sparts.\n" \
        "Please install it somewhere in your PATH to run this command." \
        % (name)
    return path


pandoc.core.PANDOC_PATH = require_binary('pandoc')
ROOT = os.path.abspath(os.path.dirname(__file__))

def read(fname):
    return open(os.path.join(ROOT, fname)).read()

def read_md_as_rest(fname):
    doc = pandoc.Document()
    doc.markdown = read(fname)
    return doc.rst

def version():
    file, pathname, description = imp.find_module('fb_dbus', [ROOT])
    return imp.load_module('fb_dbus', file, pathname, description).__version__

setup(
    name = "fb_dbus",
    version = "0.0.1",
    author = "Peter Ruibal",
    author_email = "ruibalp@gmail.com",
    description = ("An example `sparts` service that exposes Facebook's"
                   " graph API over dbus, for the rest of the OS to use"),
    license = "ISC",
    keywords = "facebook sparts service daemon dbus",
    url = "http://github.com/fmoo/facebook-dbus",
    packages = find_packages(),
    long_description=read_md_as_rest("README.md"),
    install_requires=['keyring',
                      'sparts',
                      #'dbus-python',  # dbus-python does not have setup.py :(
                      'Twisted-web'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: ISC License (ISCL)",
    ],
)

