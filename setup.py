import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "infrabin",
    version = "0.0.1",
    author = "Matteo Ruina",
    author_email = "matteo.ruina@gmail.com",
    description = ("Like httpbin, but for infrastructure."),
    license = "MIT",
    keywords = "infrastructure inf bin",
    packages=['infrabin', 'tests'],
    long_description=read('README.md'),
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)