#!/usr/bin/env python
__author__ = 'aub3'
from distutils.core import setup

setup(name='CommonCrawlLibrary',
      version='0.1',
      description='Python Distribution Utilities',
      author='Akshay Bhat',
      author_email='aub3 cornell.edu',
      url='http://www.datamininghobby.com/',
      packages=['cclib'],
      package_dir={'cclib': 'cclib'},
      package_data={'cclib': ['data/*.gz']},
     )