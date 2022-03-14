#!/usr/bin/env python
#
# Tiqit setup file
#

from distutils.core import setup

setup(name='tiqit',
      version="1.0.13",
      description='Tiqit: The Intelligent Issue Tracker',
      url='https://github.com/ensoft/tiqit',
      maintainer='Tiqit maintainers at Ensoft',
      maintainer_email='ensoft-tiqit@cisco.com',
      packages=['', 'actions', 'backend', 'frontend', 'helpers', 'pages',
                'tiqit', 'util'],
      package_dir={'': 'scripts'},
     )
