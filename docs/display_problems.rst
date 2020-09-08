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
printing the `default LED symbols`_ based on special characters::

   UnicodeEncodeError: 'ascii' codec can't encode character '\U0001f6d1' in position 2: ordinal not in range(128)

This is mainly a problem with your **locale** settings used by your terminal.

**Solution #1:** change your ``locale`` settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The best solution consists in modifying your **locale** settings since it is
permanent and you don't have to change any Python code.

1. Append ``~/.bashrc`` or ``~/.bash_profile`` with::

      export LANG="en_US.UTF-8"
      export LANGUAGE="en_US:en"

   You should provide your own **UTF-8** based locale settings. The example
   uses the English (US) locale using the **UTF-8** encoding. ``locale -a``
   gives you all the available locales on your Linux or Unix-like system.

2. Reload the ``.bashrc``::

      $ source .bashrc

3. Run the following command to make sure that your locale was set correctly::

      $ locale

      LANG="en_US.UTF-8"
      LC_COLLATE="en_US.UTF-8"
      LC_CTYPE="en_US.UTF-8"
      LC_MESSAGES="en_US.UTF-8"
      LC_MONETARY="en_US.UTF-8"
      LC_NUMERIC="en_US.UTF-8"
      LC_TIME="en_US.UTF-8"
      LC_ALL=

.. seealso::

   * `How to Set Locales (i18n) On a Linux or Unix`_: detailed article
   * `How can I change the locale?`_: from raspberrypi.stackexchange.com,
     provides answers to set the locale user and system-wide

**Solution #2:** change the default LED symbols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you are using the module :mod:`SimulRPi.GPIO` in your code, you can change
the default LED symbols used by all output channels with the function
:meth:`SimulRPi.GPIO.setdefaultsymbols`. Hence, you can provide your own
ASCII-based LED symbols using ANSI codes to color them:

.. code-block:: python
   :emphasize-lines: 4-9
   :caption: **Example:** updating the default LED symbols with ASCII characters

      import time
      import SimulRPi.GPIO as GPIO

      GPIO.setdefaultsymbols(
         {
             'ON': '\033[91m(0)\033[0m',
             'OFF': '(0)'
         }
      )
      led_channel = 11
      GPIO.setmode(GPIO.BCM)
      GPIO.setup(led_channel, GPIO.OUT)
      GPIO.output(led_channel, GPIO.HIGH)
      GPIO.cleanup()

**Output:**

.. image:: https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/solution_with_ascii_characters.png
   :target: https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/solution_with_ascii_characters.png
   :align: left
   :alt: Terminal output: ASCII characters used for LED symbols

|
|

.. seealso::

   * `Build your own Command Line with ANSI escape codes`_ : more info about
     using ANSI escape codes (e.g. color text, move the cursor up)
   * `How to print colored text in Python?`_ : from stackoverflow, lots of
     Python examples using built-in modules or third-party libraries to color
     text in the terminal.


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
   <p><b>Bad display when running the script</b></p>
   </div>

It means that you are running the script within a too small terminal window,
less than the length of a displayed line.

**Solution:** enlarge the window
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The solution is to simply enlarge your terminal window a little bit.

.. raw:: html

   <div align="center">
   <img src="https://raw.githubusercontent.com/raul23/images/master/SimulRPi/v0.1.0a0/small_window_multiple_lines_good.png"/>
   <p><b>Good display when running the script</b></p>
   </div>

**Technical explanation:** the script is supposed to display the LEDs turning
ON and OFF always on the same line. That is, when a line of LEDs is displayed,
it goes to the beginning of the line to display the next state of LEDs.

However, since the window is too small, the LEDs are being displayed on
multiple lines and when the script tries to go to the start of a line, it is
too late, it is now at another line. So you get this display of multiple lines
of LEDs.

.. URLs
.. external links
.. _Build your own Command Line with ANSI escape codes: https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
.. _How can I change the locale?: https://raspberrypi.stackexchange.com/a/19866
.. _How to print colored text in Python?: https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-python
.. _How to Set Locales (i18n) On a Linux or Unix: https://www.cyberciti.biz/faq/how-to-set-locales-i18n-on-a-linux-unix/

.. internal links
.. _default LED symbols: useful_functions.html#gpio-setdefaultsymbols