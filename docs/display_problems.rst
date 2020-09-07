================
Display problems
================



.. contents::
   :depth: 2
   :local:

ASCII characters can't be displayed
===================================

.. highlight:: none

When running the script :mod:`SimulRPi.run_examples` or using the module
:mod:`SimulRPi.GPIO` in your own code, your terminal might have difficulties
printing the `default LED symbols`_::

   UnicodeEncodeError: 'ascii' codec can't encode character '\U0001f6d1' in position 2: ordinal not in range(128)

This is mainly a problem with your ``locale`` settings used by your terminal.

**Solution #1:** change your ``locale`` settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The

**Solution #2:** change the default LED symbols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you are using the module :mod:`SimulRPi.GPIO` in your code, you can change
the default LEDs used by all output channels with the function
:meth:`SimulRPi.GPIO.setdefaultsymbols`. Hence, you can provide your own
non-ASCII LED symbols

.. code-block:: python
   :emphasize-lines: 4-9
   :caption: **Example:** updating the default LED symbols

      import time
      import SimulRPi.GPIO as GPIO

      GPIO.setdefaultsymbols(
         {
             'ON': '\033[1;31;48m(0)\033[1;37;0m',
             'OFF': '(0)'
         }
      )
      led_channel = 11
      GPIO.setmode(GPIO.BCM)
      GPIO.setup(led_channel, GPIO.OUT)
      GPIO.output(led_channel, GPIO.HIGH)
      time.sleep(0.5)
      GPIO.output(led_channel, GPIO.LOW)
      time.sleep(0.5)
      GPIO.cleanup()

**Solution #3:** ``export PYTHONIOENCODING=utf8`` (temporary solution)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Before running the script :mod:`SimulRPi.run_examples`, export the
environment variable ``PYTHONIOENCODING`` with the correct encoding::

   $ export PYTHONIOENCODING=utf8
   $ run_examples -s -e 1

However, this is **not a permanent solution** because if you use another
terminal, you will have to export ``PYTHONIOENCODING`` again before running
the script.

Multiple lines of LED symbols
=============================
When running the script :mod:`SimulRPi.run_examples`, if you get the following:

.. raw:: html

   <div align="center">
   <img src="https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/small_window_multiple_lines_bad.png"/>
   <p><b>Bad display when running the script <code>run_examples</code></b></p>
   </div>

It means that you are running the script within a too small terminal window,
less than the length of a displayed line.

**Solution:** enlarge the window
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The solution is to simply enlarge your terminal window a little bit.

.. raw:: html

   <div align="center">
   <img src="https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/small_window_multiple_lines_good.png"/>
   <p><b>Good display when running the script <code>run_examples</code></b></p>
   </div>

**Technical explanation:** the script is supposed to display the LEDs turning
ON and OFF always on the same line. That is, when a line of LEDs is displayed,
it goes to the beginning of the line to display the next state of LEDs.

However, since the window is too small, the LEDs are being displayed on
multiple lines and when the script tries to go to the start of a line, it is
too late, it is now at another line. So you get this display of multiple lines
of LEDs.

.. URLs
.. internal links
.. _default LED symbols: useful_functions.html#gpio-setdefaultsymbols