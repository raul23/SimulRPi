=========================
Useful functions from API
=========================
We present some useful functions from the `SimulRPi's API`_ along with code
examples.

.. important::

   These are functions that are available when working with the simulation
   module ``SimulRPi.GPIO``. Thus, you will always see the following import at
   the beginning of each code example presented::

      import SimulRPi.GPIO as GPIO

   Thus, the code examples are to be executed on your computer, not an RPi
   since the main reasons of these examples is to show how to use the
   ``SimulRPi`` API.

.. seealso::

   `Combine SimulRPi with RPi.GPIO`_: to know how to integrate the simulation
   module ``SimulRPi.GPIO`` with ``RPi.GPIO``

.. contents:: Contents
   :depth: 3
   :local:

``GPIO.cleanup``
================
:meth:`GPIO.cleanup` cleans up any resources at the end of your program. Very
importantly, when running in simulation, the threads responsible for displaying
"LEDs" in the terminal and listening the keyboard are stopped. Hence, we avoid
the program hanging at the end of its execution.

Here is a simple example on how to use :meth:`GPIO.cleanup` which should be
called at the end of your program:

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
:meth:`GPIO.setchannelnames` sets the channel names for multiple GPIO channels.
The channel name will be shown in the terminal along with the LED symbol for
each output channel::

   🛑  [LED 1]        🛑  [LED 2]        🛑  [LED 3]        ⬤  [lightsaber]

If no channel name is provided for a GPIO channel, its channel number will be
shown instead in the terminal.

:meth:`GPIO.setchannelnames` takes as argument a dictionary that maps channel numbers
(:obj:`int`) to channel names (:obj:`str`)::

   channel_names = {
       1: "The Channel 1",
       2: "The Channel 2"
   }

.. code-block:: python
   :emphasize-lines: 3-6
   :caption: **Example:** updating channel names for two GPIO channels

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
:meth:`GPIO.setchannels` sets the attributes for multiple GPIO channels. These
attributes are:

   * ``channel_id``: unique identifier
   * ``channel_name``: will be shown along the LED symbol in the terminal
   * ``channel_number``: GPIO channel number based on the numbering system
     you have specified (`BOARD` or `BCM`).
   * ``led_symbols``: should only be defined for output channels. It is a
     dictionary defining the symbols to be used when the LED is turned ON
     and OFF.
   * ``key``: keyboard key associated with a channel, e.g. "cmd_r".

:meth:`GPIO.setchannels` accepts as argument a list where each item is a
dictionary defining the attributes for a given GPIO channel.

This list corresponds to the main configuration's setting `gpio_channels`_.

**Example:** updating attributes for an input and output channels. Then
when the user presses ``cmd_r`` , we blink a LED for 3 seconds

.. code-block:: python
   :emphasize-lines: 6-23

      import time
      import SimulRPi.GPIO as GPIO

      key_channel = 20
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

**Output**::

   Press key 'cmd_r' to blink a LED
   Key 'cmd_r' pressed

     🔵  [The LED]

.. note::

   In the previous example, we changed the default keyboard key associated with
   the `GPIO channel 20`_ from ``ctrl_r`` to ``cmd_r``.

   .. code-block:: python
      :emphasize-lines: 1, 8

         key_channel = 20
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
:meth:`GPIO.setdefaultsymbols` sets the default LED symbols used by all output
channels. It accepts as argument a dictionary that maps each output state
('`ON`', '`OFF`') to the LED symbol (:obj:`str`)::

   default_led_symbols = {
       'ON': '🔵',
       'OFF': '⚪ '
   }

.. code-block:: python
   :emphasize-lines: 1
   :caption: **Example:** updating the default LED symbols

      import SimulRPi.GPIO as GPIO

      led_channel = 11
      GPIO.setmode(GPIO.BCM)
      GPIO.setup(led_channel, GPIO.OUT)
      GPIO.output(led_channel, GPIO.HIGH)
      GPIO.cleanup()

``GPIO.setkeymap``
==================
:meth:`GPIO.setkeymap`

``GPIO.setprinting``
====================
:meth:`GPIO.setprinting`

``GPIO.setsymbols``
===================
:meth:`GPIO.setsymbols`

``GPIO.wait``
=============
:meth:`GPIO.wait`

.. URLs
.. external links
.. TODO: IMPORTANT check link to SimulRPI github
.. _gpio_channels: https://github.com/raul23/Darth-Vader-RPi/blob/master/darth_vader_rpi/configs/default_main_cfg.json#L11
.. _GPIO channel 20: https://github.com/raul23/SimulRPi/blob/master/SimulRPi/default_keymap.py#L22

.. internal links
.. _Combine SimulRPi with RPi.GPIO: combine_simulrpi_with_rpi_gpio.html
.. _SimulRPi's API: api_reference.html
