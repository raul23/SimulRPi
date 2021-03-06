=============================
Useful functions from the API
=============================
We present some useful functions from the `SimulRPi API`_ along with code
examples.

.. important::

   These are functions that are available when working with the simulation
   module :mod:`SimulRPi.GPIO`. Thus, you will always see the following import at
   the beginning of each code example presented::

      import SimulRPi.GPIO as GPIO

   The code examples are to be executed on your computer, not on an RPi since
   the main reason for these examples is to show how to use the
   `SimulRPi API`_.

.. seealso::

   `Example: How to use SimulRPi`_: It shows you how to integrate the
   simulation module :mod:`SimulRPi.GPIO` with ``RPi.GPIO``

.. contents:: Contents
   :depth: 3
   :local:

``GPIO.cleanup``
================
:meth:`~SimulRPi.GPIO.cleanup` cleans up any resources at the end of your
program. Very importantly, when running in simulation, the threads responsible
for displaying "LEDs" in the terminal and listening to the keyboard are
stopped. Hence, we avoid the program hanging at the end of its execution.

Here is a simple example on how to use :meth:`~SimulRPi.GPIO.cleanup` which
should be called at the end of your program:

.. code-block:: python
   :emphasize-lines: 7

   import SimulRPi.GPIO as GPIO

   led_channel = 11
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(led_channel, GPIO.OUT)
   GPIO.output(led_channel, GPIO.HIGH)
   GPIO.cleanup()

**Output**::

  🛑  [11]

``GPIO.setchannelnames``
========================
:meth:`~SimulRPi.GPIO.setchannelnames` sets the channel names for multiple GPIO
channels. The channel name will be shown in the terminal along with the LED
symbol for each output channel::

   🛑  [LED 1]        🛑  [LED 2]        🛑  [LED 3]        ⬤  [lightsaber]

If no channel name is provided for a GPIO channel, its channel number will be
shown instead in the terminal.

:meth:`~SimulRPi.GPIO.setchannelnames` takes as argument a dictionary that maps
channel numbers (:obj:`int`) to channel names (:obj:`str`)::

   channel_names = {
       1: "The Channel 1",
       2: "The Channel 2"
   }

.. code-block:: python
   :emphasize-lines: 3-6
   :caption: **Example:** updating channel names for two output channels

   import SimulRPi.GPIO as GPIO

   GPIO.setchannelnames({
      10: "led 10",
      11: "led 11"
   })
   GPIO.setmode(GPIO.BCM)
   for ch in [10, 11]:
      GPIO.setup(ch, GPIO.OUT)
      GPIO.output(ch, GPIO.HIGH)
   GPIO.cleanup()

**Output**::

  🛑  [led 10]        🛑  [led 11]

``GPIO.setchannels``
====================
:meth:`~SimulRPi.GPIO.setchannels` sets the attributes for multiple GPIO
channels. These attributes are:

   * ``channel_id``: unique identifier
   * ``channel_name``: will be shown along the LED symbol in the terminal
   * ``channel_number``: GPIO channel number based on the numbering system
     you have specified (`BOARD` or `BCM`).
   * ``led_symbols``: should only be defined for output channels. It is a
     dictionary defining the symbols to be used when the LED is turned ON
     and turned OFF.
   * ``key``: should only be defined for input channels. The names of keyboard
     keys that you can use are those specified in the
     `SimulRPi's API documentation`_, e.g. `media_play_pause`, `shift`, and
     `shift_r`.

:meth:`~SimulRPi.GPIO.setchannels` accepts as argument a list where each item
is a dictionary defining the attributes for a given GPIO channel.

**Example:** updating attributes for an input and output channels. Then
when the user presses ``cmd_r``, we blink a LED for 3 seconds

.. code-block:: python
   :emphasize-lines: 6-23

      import time
      import SimulRPi.GPIO as GPIO

      key_channel = 23
      led_channel = 10
      gpio_channels = [
         {
             "channel_id": "button",
             "channel_name": "The button",
             "channel_number": key_channel,
             "key": "cmd_r"
         },
         {
             "channel_id": "led",
             "channel_name": "The LED",
             "channel_number": led_channel,
             "led_symbols": {
                 "ON": "🔵",
                 "OFF": "⚪ "
             }
         }
      ]
      GPIO.setchannels(gpio_channels)
      GPIO.setmode(GPIO.BCM)
      GPIO.setup(key_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
      GPIO.setup(led_channel, GPIO.OUT)
      print("Press key 'cmd_r' to blink a LED")
      while True:
         try:
             if not GPIO.input(key_channel):
                 print("Key 'cmd_r' pressed")
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

**Output:** blinking not shown ::

   Press key 'cmd_r' to blink a LED
   Key 'cmd_r' pressed

     🔵  [The LED]

.. note::

   In the previous example, we changed the default keyboard key associated with
   the `GPIO channel 23`_ from ``media_volume_mute`` to ``cmd_r``.

   .. code-block:: python
      :emphasize-lines: 1, 8

         key_channel = 23
         led_channel = 10
         gpio_channels = [
            {
                "channel_id": "button",
                "channel_name": "The button",
                "channel_number": key_channel,
                "key": "cmd_r"
            },
          ...

``GPIO.setdefaultsymbols``
==========================
:meth:`~SimulRPi.GPIO.setdefaultsymbols` sets the default LED symbols used by
**all output** channels. It accepts as argument a dictionary that maps an
output state ('`ON`', '`OFF`') to a LED symbol (:obj:`str`).

By default, these are the LED symbols used by all output channels::

   default_led_symbols = {
       'ON': '🛑',
       'OFF': '⚪'
   }

The next example shows you how to change these default LED symbols with the
function :meth:`~SimulRPi.GPIO.setdefaultsymbols`

.. code-block:: python
   :emphasize-lines: 4-9
   :caption: **Example:** updating the default LED symbols and toggling a LED

      import time
      import SimulRPi.GPIO as GPIO

      GPIO.setdefaultsymbols(
         {
             'ON': '🔵',
             'OFF': '⚪ '
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

**Output:** blinking not shown ::

  🔵   [11]

``GPIO.setkeymap``
==================
:meth:`~SimulRPi.GPIO.setkeymap` sets the `default keymap dictionary`_ with a
new mapping between keyboard keys and channel numbers.

It takes as argument a dictionary mapping keyboard keys (:obj:`str`) to GPIO
channel numbers (:obj:`int`)::

   key_to_channel_map = {
       "cmd": 23,
       "alt_r": 24,
       "ctrl_r": 25
   }

.. code-block:: python
   :emphasize-lines: 4-6
   :caption: **Example:** `by default`_, ``cmd_r`` is mapped to channel 17.
             We change this mapping by associating ``ctrl r`` to channel 17.

   import SimulRPi.GPIO as GPIO

   channel = 17
   GPIO.setkeymap({
      'ctrl_r': channel
   })
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
   print("Press key 'ctrl_r' to exit")
   while True:
      if not GPIO.input(channel):
          print("Key 'ctrl_r' pressed!")
          break
   GPIO.cleanup()

**Output**::

   Press key 'ctrl_r' to exit
   Key 'ctrl_r' pressed!


``GPIO.setprinting``
====================
:meth:`~SimulRPi.GPIO.setprinting` enables or disables printing the LED symbols
and channel names/numbers to the terminal.

.. code-block:: python
   :emphasize-lines: 3
   :caption: **Example:** disable printing to the terminal

   import SimulRPi.GPIO as GPIO

   GPIO.setprinting(False)
   led_channel = 11
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(led_channel, GPIO.OUT)
   GPIO.output(led_channel, GPIO.HIGH)
   GPIO.cleanup()

``GPIO.setsymbols``
===================
:meth:`~SimulRPi.GPIO.setsymbols` sets the LED symbols for multiple **output**
channels. It takes as argument a dictionary mapping channel numbers
(:obj:`int`) to LED symbols (:obj:`dict`)::

   led_symbols = {
       1: {
           'ON': '🔵',
           'OFF': '⚪ '
       },
       2: {
           'ON': '🔵',
           'OFF': '⚪ '
       }
   }

There is a LED symbol for each output state (`ON` and `OFF`) for a given output
channel.

.. code-block:: python
   :emphasize-lines: 4-9
   :caption: **Example:** set the LED symbols for a GPIO channel

      import time
      import SimulRPi.GPIO as GPIO

      GPIO.setsymbols({
         11: {
             'ON': '🔵',
             'OFF': '⚪ '
         }
      })
      led_channel = 11
      GPIO.setmode(GPIO.BCM)
      GPIO.setup(led_channel, GPIO.OUT)
      GPIO.output(led_channel, GPIO.HIGH)
      time.sleep(0.5)
      GPIO.output(led_channel, GPIO.LOW)
      time.sleep(0.5)
      GPIO.cleanup()

**Output:** blinking not shown ::

  🔵   [11]

``GPIO.wait``
=============
:meth:`~SimulRPi.GPIO.wait` waits for the threads to do their tasks. If there
was an exception caught by one of the threads, then it is raised by
:meth:`~SimulRPi.GPIO.wait`.

Thus it is ideal for :meth:`~SimulRPi.GPIO.wait` to be called within a ``try``
block after you are done with the :mod:`SimulRPi.GPIO` API::

   try:
       do_something_with_gpio_api()
       GPIO.wait()
   except Exception as e:
       # Do something with error
   finally:
      GPIO.cleanup()

:meth:`~SimulRPi.GPIO.wait` takes as argument the number of seconds you want to
wait at most for the threads to accomplish their tasks.

**Example:** wait for the threads to do their jobs and if there is an exception
in one of the threads' target function or callback, it will be caught in our
``except`` block.

.. code-block:: python
   :emphasize-lines: 13

   import time
   import SimulRPi.GPIO as GPIO

   try:
      led_channel = 11
      GPIO.setmode(GPIO.BCM)
      GPIO.setup(led_channel, GPIO.OUT)
      GPIO.output(led_channel, GPIO.HIGH)
      GPIO.wait(1)
   except Exception as e:
      # Could be an exception raised in a thread's target function or callback
      # from SimulRPi library
      print(e)
   finally:
      GPIO.cleanup()

.. important::

   If we don't use :meth:`~SimulRPi.GPIO.wait` in the previous example, we
   won't be able to catch any exception occurring in a thread's target function
   or callback since the threads `simply catch and save the exceptions`_ but
   don't raise them. :meth:`~SimulRPi.GPIO.wait` takes care of raising an
   exception if it was already caught and saved by a thread.

   Also, the reason for not raising the exception within a thread's ``run``
   method or its callback is because the main program will not be able to
   catch it. The thread's exception needs to be raised outside of the thread's
   ``run`` method or callback so the main program can further catch it. And
   this is what :meth:`~SimulRPi.GPIO.input`, :meth:`~SimulRPi.GPIO.output`,
   and :meth:`~SimulRPi.GPIO.wait` do: they raise the thread's exception so the
   main program can catch it and process it down the line.

   See `Test threads raising exceptions`_ about some tests done to check what
   happens when a thread raises an exception within its ``run`` method or
   callback (**spoiler:** not good!).

.. URLs
.. default cfg files
.. _by default: https://github.com/raul23/archive/blob/master/SimulRPi/v0.1.0a0/default_keymap.py#L19
.. _GPIO channel 23: https://github.com/raul23/archive/blob/master/SimulRPi/v0.1.0a0/default_keymap.py#L25

.. external links
.. _Test threads raising exceptions: https://github.com/raul23/SimulRPi/blob/master/docs/test_threads_exception.rst

.. internal links
.. _default keymap dictionary: api_reference.html#content-default-keymap-label
.. _simply catch and save the exceptions: api_reference.html#SimulRPi.manager.DisplayExceptionThread.run
.. _Example\: How to use SimulRPi: example.html
.. _SimulRPi API: api_reference.html
.. _SimulRPi's API documentation: api_reference.html#content-default-keymap-label
