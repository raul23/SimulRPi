"""Package that defines modules for testing the `SimulRPi` package.

The command to execute the :mod:`unittest` test runner::

    $ python -m unittest discover

This command is executed at the root of the project directory and all tests in
`tests/` will be run.

Also, to execute a specific test, this is the command::

    $ python -m unittest tests/test_module.py

This command is executed at the root of the project directory.

"""

from pyutils import install_colored_logger
install_colored_logger()
