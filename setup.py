"""setup.py file for the package ``SimulRPi.GPIO``.

The PyPi project name is ``SimulRPi.GPIO`` and package name is ``SimulRPi``.

"""

import os
import sys
from setuptools import find_packages, setup

from SimulRPi import __version__, __test_version__


# Choose the correct version based on script's arg
if sys.argv[1] == "testing":
    VERSION = __test_version__
    # Remove "testing" from args so setup doesn't process "testing" as a cmd
    sys.argv.remove("testing")
else:
    VERSION = __version__

# Directory of this file
dirpath = os.path.abspath(os.path.dirname(__file__))

# The text of the README file (used on PyPI)
with open(os.path.join(dirpath, "README_pypi.rst")) as f:
    README = f.read()

# The text of the requirements.txt file
with open(os.path.join(dirpath, "requirements.txt")) as f:
    REQUIREMENTS = f.read().split()

# TODO: Documentation should point to correct version of project at the moment?
setup(name='SimulRPi',
      version=VERSION,
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
      project_urls={  # Optional
          'Bug Reports': 'https://github.com/raul23/SimulRPi/issues',
          'Documentation': 'https://simulrpi.readthedocs.io/en/latest/index.html',
          'Source': 'https://github.com/raul23/SimulRPi',
        },
      zip_safe=False)
