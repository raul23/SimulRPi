"""setup.py file for the package `SimulRPi.GPIO`.

The PyPi project name is `SimulRPi.GPIO` and package name is `SimulRPi`.

"""

import os
from setuptools import find_packages, setup

from SimulRPi import __version__


# Directory of this file
dirpath = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(dirpath, "README.rst")) as f:
    README = f.read()

setup(name='SimulRPi',
      version=__version__,
      description='WRITEME',
      long_description=README,
      long_description_content_type='text/x-rst',
      classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
      ],
      keywords='python raspberrypi rpi library simulation',
      url='https://github.com/raul23/SimulRPi',
      author='Raul C.',
      author_email='rchfe23@gmail.com',
      license='GPLv3',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      install_requires=[
          'pynput'
      ],
      zip_safe=False)
