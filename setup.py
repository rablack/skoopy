"""Skoobot control module setup
"""

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

setup(
    name='skoopy',
    version='0.1.0.dev1',
    description='Skoobot control module',
    license='MIT',
    url='https://github.com/rablack/skoopy',
    author='Robert Black',
    packages=find_packages(exclude=['tests']),
)
