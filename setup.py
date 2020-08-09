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

# The text of the requirements.txt file
with open(os.path.join(dirpath, "requirements.txt")) as f:
    REQUIREMENTS = f.read().split()

setup(name='SimulRPi',
      version=__version__,
      description='A library that partly fakes RPi.GPIO and simulates some I/O '
                  'devices on a Raspberry Pi.',
      long_description=README,
      long_description_content_type='text/x-rst',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',

      ],
      keywords='Raspberry Pi GPIO pynput library simulation mock',
      url='https://github.com/raul23/SimulRPi',
      author='Raul C.',
      author_email='rchfe23@gmail.com',
      license='GPLv3',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      install_requires=REQUIREMENTS,
      entry_points={
          'console_scripts': ['run_examples=SimulRPi.run_examples:main']
      },
      zip_safe=False)
