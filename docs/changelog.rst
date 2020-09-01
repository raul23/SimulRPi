=========
Changelog
=========

0.0.1a0
=======
* In ``SimulRPi.GPIO``, the package ``pynput`` is not required anymore. If it
  is not found, all keyboard-related functionalities from the ``SimulRPi``
  library will be skipped. Thus, no keyboard keys will be detected if pressed
  or released when ``pynput`` is not installed.

  This was necessary because *Travis* was raising an exception when I was
  running a unit test: `Xlib.error.DisplayNameError`_. It was
  due to ``pynput`` not working well in a headless setup. Thus, ``pynput`` is
  now removed from *requirements_travis.txt*.

  Eventually, I will mock ``pynput`` when doing unit tests on parts of the
  library that make use of ``pynput``.

* Started writing unit tests

0.0.0a0
=======
* First version

* Tested `code examples`_ on different platforms and here are the results
   * On an RPi with ``RPi.GPIO``: all examples involving LEDs and pressing
     buttons worked
   * On a computer with ``SimulRPi.GPIO``
      * macOS: all examples involving "LEDs" and keyboard keys worked
      * RPi OS [Debian-based]: all examples involving "LEDs" only worked

        **NOTE:** I was running the script :mod:`run_examples`
        with ``ssh`` but ``pynput`` doesn't detect any pressed keyboard keys
        even though I set my environment variable ``Display``, added
        ``PYTHONPATH`` to *etc/sudoers* and ran the script with ``sudo``. To be
        further investigated.

.. URLs

.. 1. External links
.. _Xlib.error.DisplayNameError: https://travis-ci.org/github/raul23/SimulRPi/builds/716458786#L235

.. 2. Internal links
.. _code examples: README_docs.html#examples-label
