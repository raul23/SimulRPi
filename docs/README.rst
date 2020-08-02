======
README
======
.. raw:: html

   <p align="center"><img src="https://raw.githubusercontent.com/raul23/SimulRPi/master/docs/_static/images/SimulRPi_logo.png"></p>

.. image:: https://readthedocs.org/projects/simulrpi/badge/?version=latest
   :target: https://simulrpi.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://travis-ci.org/raul23/SimulRPi.svg?branch=master
   :target: https://travis-ci.org/raul23/SimulRPi
   :alt: Build Status

**SimulRPi** is a library that partly fakes
`RPi.GPIO <https://pypi.org/project/RPi.GPIO/>`_ and simulates some I/O devices
on a Raspberry Pi.

It simulates these I/O devices connected to a Raspberry Pi:

- push buttons by listening to keys pressed/released on the keyboard and
- LEDs by displaying small dots blinking on the terminal along with their GPIO pin number.

When a LED is turned on, it is shown as a small red circle on the terminal. The
package `pynput`_ is used to monitor the keyboard for any key pressed.

.. highlight:: none

**Example: terminal output** ::

    o [11]   o [9]   o [10]

.. highlight:: python

where each circle represents a LED (here they are all turned off) and the number
between brackets is the associated GPIO pin number.
