import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "fb_dbus",
    version = "0.0.1",
    author = "Peter Ruibal",
    author_email = "ruibalp@gmail.com",
    description = ("An example `sparts` service that exposes Facebook's"
                   " graph API over dbus, for the rest of the OS to use"),
    license = "ISC",
    keywords = "facebook sparts service daemon dbus",
    url = "http://github.com/fmoo/fb_dbus",
    packages = find_packages(),
    long_description=read('README'),
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

