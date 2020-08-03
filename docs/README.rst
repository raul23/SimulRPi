======
README
======
.. image:: https://raw.githubusercontent.com/raul23/SimulRPi/master/docs/_static/images/SimulRPi_logo.png
   :target: https://raw.githubusercontent.com/raul23/SimulRPi/master/docs/_static/images/SimulRPi_logo.png
   :align: center
   :alt: SimulRPi logo

.. image:: https://readthedocs.org/projects/simulrpi/badge/?version=latest
   :target: https://simulrpi.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
   :align: left

.. image:: https://travis-ci.org/raul23/SimulRPi.svg?branch=master
   :target: https://travis-ci.org/raul23/SimulRPi
   :alt: Build Status
   :align: left

**SimulRPi** is a library that partly fakes
`RPi.GPIO <https://pypi.org/project/RPi.GPIO/>`_ and simulates some I/O devices
on a Raspberry Pi (RPi).

It simulates these I/O devices connected to a Raspberry Pi:

- push buttons by listening to keys pressed/released on the keyboard and
- LEDs by displaying small dots blinking on the terminal along with their GPIO \
  pin number.

When a LED is turned on, it is shown as a small red circle on the terminal. The
package `pynput <https://pynput.readthedocs.io/>`_ is used to monitor the
keyboard for any pressed key.

**Example: terminal output**

.. image:: https://raw.githubusercontent.com/raul23/images/master/Darth-Vader-RPi/terminal_leds_active.gif
   :target: https://raw.githubusercontent.com/raul23/images/master/Darth-Vader-RPi/terminal_leds_active.gif
   :align: center
   :alt: Simulating LEDs on an RPi via a terminal

Each circle represents a LED blinking on an RPi and the number between brackets 
is the associated GPIO channel number. Here the "LED" on channel 22 toggles
between on and off when a key is pressed.
