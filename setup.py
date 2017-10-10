"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name='infrabin',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.4',

    description='Like httpbin, but for infrastructure',

    # The project's main homepage.
    url='https://github.com/maruina/infrabin',

    # Author details
    author='Matteo Ruina',
    author_email='matteo.ruina@gmail.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Test Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='infrastructure tests',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages("src", exclude=['contrib', 'docs', 'tests']),
    package_dir={'': 'src'},
    install_requires=['Flask', 'requests', 'Flask-Caching', 'waitress',
                      'netifaces', 'dnspython', 'decorator', 'six'],
    setup_requires=['pytest-runner'],
    tests_requires=['pytest', 'pytest-flask', 'tox'],
    entry_points='''
         [console_scripts]
         infrabin=infrabin.scripts.cli:infrabin
         '''
)
