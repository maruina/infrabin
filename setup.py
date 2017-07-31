import os
from setuptools import setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = "infrabin",
    version = "0.0.1",
    author = "Matteo Ruina",
    author_email = "matteo.ruina@gmail.com",
    description = ("Like httpbin, but for infrastructure."),
    license = "MIT",
    keywords = "infrastructure bin",
    packages=['infrabin', 'tests'],
    long_description=long_description,
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    setup_requires=['pytest-runner'],
    install_requires = ['Flask'],
    tests_require=['pytest', 'pytest-flask']
)