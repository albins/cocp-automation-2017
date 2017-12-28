from setuptools import setup

import conductor

setup(
    name='conductor',

    # Uses semver
    version=conductor.__version__,

    description='Automation tools for the COCP course (and others)',
    long_description="",

    url='',

    # Author details
    author='Albin Stjerna',
    author_email='albin.stjerna@gmail.com',
    license="GPLv3",
    packages=['conductor'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],

    install_requires=['matplotlib', 'cerberus', 'pyyaml', 'daiquiri', 'jinja2'],
    scripts=['bin/conductor',
             'bin/merge_tables.py',
             'bin/graph_table.py',
             'bin/runner.py',
             'conductor/gather_stats.py'],
)
