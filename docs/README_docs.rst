======
README
======

.. _code examples: https://simulrpi.readthedocs.io/en/latest/api_reference.html#module-run_examples
.. _Darth-Vader-RPi: https://github.com/raul23/Darth-Vader-RPi
.. _install: #installation-instructions
.. _let me know through SimulRPi's issues page:
    https://github.com/raul23/SimulRPi/issues
.. _pynput: https://pynput.readthedocs.io/
.. _RPi.GPIO: https://pypi.org/project/RPi.GPIO/
.. _run_examples: https://simulrpi.readthedocs.io/en/latest/api_reference.html#module-run_examples
.. _run_examples.py: #script-run-examples-py
.. _SimulRPi documentation: https://simulrpi.readthedocs.io/en/latest/index.html
.. _SimulRPi GitHub: https://github.com/raul23/SimulRPi
.. _SimulRPi PyPI: https://pypi.org/project/SimulRPi/
.. _SimulRPi.GPIO: https://pypi.org/project/SimulRPi/

.. raw:: html

   <p align="center"><img src="https://raw.githubusercontent.com/raul23/SimulRPi/master/docs/_static/images/SimulRPi_logo.png">
   <br>🚧 &nbsp;&nbsp;&nbsp;<b>Work-In-Progress</b>
   </p>

.. image:: https://readthedocs.org/projects/simulrpi/badge/?version=latest
   :target: https://simulrpi.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://travis-ci.org/raul23/SimulRPi.svg?branch=master
   :target: https://travis-ci.org/raul23/SimulRPi
   :alt: Build Status

**SimulRPi** is a Python library that partly fakes
`RPi.GPIO <https://pypi.org/project/RPi.GPIO/>`_ and simulates some I/O devices
on a Raspberry Pi (RPi).

.. raw:: html

   <div align="center">
   <img src="https://raw.githubusercontent.com/raul23/images/master/Darth-Vader-RPi/simulation_terminal_channel_number_430x60.gif"/>
   <p><b>Simulating LEDs on an RPi via a terminal</b></p>
   </div>

.. contents::
   :depth: 3
   :local:

Introduction
============
In addition to partly faking `RPi.GPIO <https://pypi.org/project/RPi.GPIO/>`_,
**SimulRPi** also simulates these I/O devices connected to an RPi:

- push buttons by listening to pressed keyboard keys and
- LEDs by displaying small dots blinking on the terminal along with their GPIO \
  pin number.

When a LED is turned on, it is shown as a red dot in the terminal. The package
`pynput`_ is used to monitor the keyboard for any pressed key.

**Example: terminal output**

.. raw:: html

   <div align="center">
   <img src="https://raw.githubusercontent.com/raul23/images/master/Darth-Vader-RPi/simulation_terminal_channel_number_430x60.gif"/>
   <p><b>Simulating LEDs on an RPi via a terminal</b></p>
   </div>

Each dot represents a blinking LED connected to an RPi and the number
between brackets is the associated GPIO channel number. Here the "LED" on
channel 22 toggles between on and off when a key is pressed.

Also, the color of the LEDs can be customized as you can see here where the LED
on Channel 22 is colored differently from the others.

.. important::

   This library is not a Raspberry Pi emulator nor a complete mock-up of
   `RPi.GPIO`_, only the most important functions that I needed for my
   `Darth-Vader-RPi`_ project were added.

   If there is enough interest in this library, I will eventually mock more
   functions from `RPi.GPIO`_. Thus,
   `let me know through SimulRPi's issues page`_ if you want me to add more
   things to this library.

Dependencies
============
* **Platforms:** macOS, Linux
* **Python**: 3.5, 3.6, 3.7, 3.8
* ``pynput`` >=1.6.8: for monitoring the keyboard for any pressed key

Installation instructions
=========================
1. Install the ``SimulRPi`` package with *pip*::

   $ pip install SimulRPi

   It will install the dependency ``pynput`` if it is not already found in your system.

2. Test your installation by importing ``SimulRPi`` and printing its version::

   $ python -c "import SimulRPi; print(SimulRPi.__version__)"

Usage
=====
Use the library in your own code
--------------------------------
Case 1: with a ``try`` and ``except`` blocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can try importing ``RPi.GPIO`` first and if it is not found, then fallback
on the module ``SimulRPi.GPIO``.

..
   IMPORTANT:
   GitHub and PyPI don't recognize `:mod:`
   Also they don't recognize :caption: (used in code-block)

.. code-block:: python
   :caption: **Case 1:** with a ``try`` and ``except`` blocks

   try:
       import RPi.GPIO as GPIO
   except ImportError:
       import SimulRPi.GPIO as GPIO

   # Rest of your code

The code from the previous example would be put at the beginning of your file
with the other imports.

Case 2: with a simulation flag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Or maybe you have a flag to tell whether you want to work with the simulation
module or the real one.

.. code-block:: python
   :caption: **Case 2:** with a simulation flag

   if simulation:
       import SimulRPi.GPIO as GPIO
   else:
       import RPi.GPIO as GPIO

   # Rest of your code

Script ``run_examples.py``
--------------------------
The script `run_examples`_ which you have access to once you
`install`_ the ``SimulRPi`` package allows you to run different code examples on
your RPi or computer. If it is run on your computer, it will make use of the
module `SimulRPi.GPIO`_ which partly fakes `RPi.GPIO`_.

The different code examples are those presented in `Examples <#id4>`_ and
show the capability of ``SimulRPi.GPIO`` for simulating I/O devices on an RPi
such as push buttons and LEDS.

Here is a list of the functions associated with each code example:

   - Example 1: :meth:`run_examples.ex1_turn_on_led`
   - Example 2: :meth:`run_examples.ex2_turn_on_many_leds`
   - Example 3: :meth:`run_examples.ex3_detect_button`
   - Example 4: :meth:`run_examples.ex4_blink_led`
   - Example 5: :meth:`run_examples.ex5_blink_led_if_button`

List of options
~~~~~~~~~~~~~~~

To display the script's list of options and their descriptions:
``run_examples -h``

   -e       The number of the code example you want to run. It is required.
            (default: None)
   -m       Set the numbering system used to identify the I/O pins on an RPi.
            (default: BCM)
   -s       Enable simulation mode, i.e. ``SimulRPi.GPIO`` wil be use for
            simulating ``RPi.GPIO``. (default: False)
   -l       The GPIO channels to be used for LEDs. If an example only requires
            1 channel, the first channel from the provided list will be used.
            (default: [10, 11, 12])
   -b       The GPIO channel to be used for a push button. The default value is
            channel 20 which is associated with the keyboard key *alt_r*.
            (default: 13)
   -t       Total time in seconds LEDs will be blinking. (default: 4)
   -k       The name of the key associated with the button channel. The name
            must be one of those recognized by the module *pynput*. See the
            *SimulRPi* documentation for a list of valid key names:
            https://bit.ly/2Pw1OBe. Example: *alt*, *cmd_r* (default: *alt_r*)
   --on     Time in seconds the LEDs will stay turned ON at a time. (default: 1)
   --off    Time in seconds the LEDs will stay turned OFF at a time. (default: 1)

How to run the script
~~~~~~~~~~~~~~~~~~~~~
Once you install the package ``SimulRPi`` (see `Installation Instructions
<#installation-instructions>`_), you should have access to the script
``run_examples`` which can be called from the terminal by providing some
arguments.

For example: ``run_examples -e 1 -s``.

Let's run the code example **# 5** which blinks a LED if a specified key is
pressed.

Here is the command line for blinking a LED (on channel 21) for a total of 5
seconds if the key ``cmd_r`` is pressed and if running in simulation::

   $ run_examples -s -e 5 -l 21 -t 5 -k cmd_r

**Output:**

.. image:: https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/run_examples_05_terminal_output.gif
   :target: https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/run_examples_05_terminal_output.gif
   :align: left
   :alt: Example 05: terminal output

|
|
|
|

.. important::

   Don't forget the flag *-s* (for simulation) when running the script
   ``run_examples`` if you want to run a code example on your computer, and
   not on your RPi.

Examples
========
The examples presented thereafter will show you how to use ``SimulRPi`` to
simulate LEDs and push buttons.

The code for the examples shown here can be also found as a script in
`run_examples`_.

.. note::

   Since we are showing how to use the ``SimulRPi`` library, the presented code
   examples are to be executed on your computer. However, the script
   `run_examples.py`_ which runs the following code examples can be executed on a
   Raspberry Pi or your computer.

Example 1: display 1 LED
------------------------
**Example 1** consists in displaying one LED on the GPIO channel 11. Here is
the code along with the output from the terminal:

.. code-block:: python

   import SimulRPi.GPIO as GPIO

   led_channel = 11
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(led_channel, GPIO.OUT)
   GPIO.output(led_channel, GPIO.HIGH)
   GPIO.cleanup()

**Output:**

.. image:: https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/example_01_terminal_output.png
   :target: https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/example_01_terminal_output.png
   :align: left
   :alt: Example 01: terminal output

|
|
|

The command line for reproducing the same results for example 1 with the script
``run_examples`` is the following::

   $ run_examples -s -e 1 -l 11

.. warning::

   Always call `GPIO.cleanup() <https://simulrpi.readthedocs.io/en/latest/api_reference.html#GPIO.cleanup>`_
   at the end of your program to free up any resources such as stopping threads.

Example 2: display 3 LEDs
-------------------------
**Example 2** consists in displaying three LEDs on channels 10, 11, and 12,
respectively. Here is the code along with the output from the terminal:

.. code-block:: python

   import SimulRPi.GPIO as GPIO

   led_channels = [10, 11, 12]
   GPIO.setmode(GPIO.BCM)
   for ch in led_channels:
       GPIO.setup(ch, GPIO.OUT)
       GPIO.output(ch, GPIO.HIGH)
   GPIO.cleanup()

**Output:**

.. image:: https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/example_02_terminal_output.png
   :target: https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/example_02_terminal_output.png
   :align: left
   :alt: Example 02: terminal output

|
|

The command line for reproducing the same results for example 2 with the script
``run_examples`` is the following::

   $ run_examples -s -e 2

Example 3: detect a pressed key
-------------------------------
**Example 3** consists in detecting if the key ``cmd_r`` is pressed and then
printing a message. Here is the code along with the output from the terminal:

.. code-block:: python

   import SimulRPi.GPIO as GPIO

   channel = 17
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
   print("Press key 'cmd_r' to exit")
   while True:
       if not GPIO.input(channel):
           print("Key 'cmd_r' pressed")
           break
   GPIO.cleanup()


**Output:**

.. image:: https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/example_03_terminal_output.png
   :target: https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/example_03_terminal_output.png
   :align: left
   :alt: Example 03: terminal output

|
|
|

The command line for reproducing the same results for example 3 with the script
``run_examples`` is the following::

   $ run_examples -s -e 3 -k cmd_r

.. note::

   By default, ``SimulRPi`` maps the key ``cmd_r`` to channel 17 as can be
   seen from the `default key-to-channel map
   <https://github.com/raul23/SimulRPi/blob/master/SimulRPi/default_keymap.py#L19>`_.

   See also the documentation for `SimulRPi.mapping <https://simulrpi.readthedocs.io/en/latest/api_reference.html#module-SimulRPi.mapping>`_
   where the default keymap is defined.

Example 4: blink a LED
----------------------
**Example 4** consists in blinking a LED on channel 20 for 4 seconds (or until
you press ``ctrl`` + ``c``). Here is the code along with the output from
the terminal:

.. code-block:: python

   import time
   import SimulRPi.GPIO as GPIO

   channel = 20
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(channel, GPIO.OUT)
   start = time.time()
   print("Start")
   while (time.time() - start) < 4:
       try:
           GPIO.output(channel, GPIO.HIGH)
           time.sleep(0.5)
           GPIO.output(channel, GPIO.LOW)
           time.sleep(0.5)
       except KeyboardInterrupt:
           break
   GPIO.cleanup()
   print("\nEnd")

**Output:**

.. image:: https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/example_04_terminal_output.gif
   :target: https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/example_04_terminal_output.gif
   :align: left
   :alt: Example 04: terminal output

|
|
|

The command line for reproducing the same results for example 4 with the script
``run_examples`` is the following::

   $ run_examples -s -e 4 -t 4 -l 20

Example 5: blink a LED if a key is pressed
------------------------------------------
**Example 5** consists in blinking a LED on channel 10 for 3 seconds if the key
``ctrl_r`` is pressed. And then, exiting from the program. The program can
also be terminated at any time by pressing ``ctrl`` + ``c``. Here is the
code along with the output from the terminal:

.. code-block:: python

   import time
   import SimulRPi.GPIO as GPIO

   led_channel = 10
   key_channel = 20
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(led_channel, GPIO.OUT)
   GPIO.setup(key_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
   print("Press key 'ctrl_r' to blink a LED")
   while True:
       try:
           if not GPIO.input(key_channel):
               print("Key 'ctrl_r' pressed")
               start = time.time()
               while (time.time() - start) < 3:
                   GPIO.output(led_channel, GPIO.HIGH)
                   time.sleep(0.5)
                   GPIO.output(led_channel, GPIO.LOW)
                   time.sleep(0.5)
               break
       except KeyboardInterrupt:
           break
   GPIO.cleanup()

**Output:**

.. image:: https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/example_05_terminal_output.gif
   :target: https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/example_05_terminal_output.gif
   :align: left
   :alt: Example 05: terminal output

|
|
|

The command line for reproducing the same results for example 5 with the script
``run_examples`` is the following::

   $ run_examples -s -e 5 -t 3 -k ctrl_r

.. note::

   By default, ``SimulRPi`` maps the key ``ctrl_r`` to channel 20 as can be
   from the `default key-to-channel map
   <https://github.com/raul23/SimulRPi/blob/master/SimulRPi/default_keymap.py#L22>`__.

   See also the documentation for `SimulRPi.mapping <https://simulrpi.readthedocs.io/en/latest/api_reference.html#module-SimulRPi.mapping>`_
   where the default keymap is defined.

Change Log
==========
0.0.1a0
-------
* In ``SimulRPi.GPIO``, the package ``pynput`` is not required anymore. If it
  is not found, all keyboard-related functionalities from the ``SimulRPi``
  library will be skipped. Thus, no keyboard keys will be detected if pressed
  or released when ``pynput`` is not installed.

  This was necessary because *Travis* was raising an exception when I was
  running a unit test: `Xlib.error.DisplayNameError
  <https://travis-ci.org/github/raul23/SimulRPi/builds/716458786#L235>`_. It was
  due to ``pynput`` not working well in a headless setup. Thus, ``pynput`` is
  now removed from *requirements_travis.txt*.

  Eventually, I will mock ``pynput`` when doing unit tests on parts of the
  library that make use of ``pynput``.

* Started writing unit tests

0.0.0a0
-------
* First version

* Tested code `examples <#id4>`__ on different platforms and here are the results
   * On an RPi with ``RPi.GPIO``: all examples involving LEDs and pressing
     buttons worked
   * On a computer with ``SimulRPi.GPIO``
      * macOS: all examples involving "LEDs" and keyboard keys worked
      * RPi OS [Debian-based]: all examples involving only "LEDs" worked

        **NOTE:** I was running the script :mod:`run_examples`
        with ``ssh`` but ``pynput`` doesn't detect any pressed keyboard keys
        even though I set my environment variable ``Display``, added
        ``PYTHONPATH`` to *etc/sudoers* and ran the script with ``sudo``. To be
        further investigated.

Resources
=========
* `SimulRPi GitHub`_: source code
* `SimulRPi PyPI`_
* `Darth-Vader-RPi`_: personal project using ``RPi.GPIO`` for activating a Darth
  Vader action figure with light and sounds and ``SimulRPi.GPIO`` as fallback if
  testing on a computer when no RPi available

References
==========
* `pynput`_: package used for monitoring the keyboard for any pressed key as to
  simulate push buttons connected to an RPi
* `RPi.GPIO`_: a module to control RPi GPIO channels
