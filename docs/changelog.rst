=========
Changelog
=========

.. contents::
   :depth: 2
   :local:

0.1.0a0
=======
.. _default-led-symbols-label:

* The default LED symbols are now big non-ASCII signs::

   🛑 : LED turned ON
   ⚪ : LED turned OFF

  **NOTE:** the default symbols used by all GPIO channels can be modified with
  :meth:`GPIO.setdefaultsymbols`

* LED symbols for each channel can be modified with :meth:`GPIO.setsymbols`
* Channel names can now be displayed instead of channel numbers in the terminal::

   🛑  [LED 1]        🛑  [LED 2]        🛑  [LED 3]        ⬤  [lightsaber]
* New attributes:

  * :attr:`Pin.channel_id`: unique identifier
  * :attr:`Pin.channel_name`: displayed in the terminal along each LED symbol
  * :attr:`Pin.channel_number`: used to be called ``channel``
  * :attr:`Pin.led_symbols`: each pin (aka channel) is represented by a LED
    symbol if it is an output channel
  * :attr:`Manager.default_led_symbols`: by default these are the
    `LED symbols`_ used to represent each GPIO channel in the terminal

* New functions:

  * :meth:`GPIO.setchannelnames`: set channels names for multiple channels
  * :meth:`GPIO.setchannels`: set the attributes (e.g. ``channel_name`` and
    ``led_symbols``) for multiple channels
  * :meth:`GPIO.setdefaultsymbols`: change the default LED symbols
  * :meth:`GPIO.setsymbols`: set the LED symbols for multiple channels
  * :meth:`GPIO.wait`: waits for the threads to do their tasks and raises an
    exception if there is an error in a thread's target function. It can be
    used as a context manager.

* The displaying thread is now an instance of :class:`GPIO.ExceptionThread`.
  Thus, if there is an exception raised in :meth:`GPIO.Manager.display_leds()`,
  it is now possible to catch it in a main thread

* The keyboard listener thread is now an instance of
  ``GPIO.KeyboardExceptionThread`` (a subclass of
  :class:`pynput.keyboard.Listener`). Thus, if there an exception raised in
  :meth:`GPIO.Manager.on_press` or :meth:`GPIO.Manager.on_release`, it is now
  possible to catch it in a main thread

* :mod:`run_examples`: all simulation-based examples involving "LEDs" and
  pressing keyboard keys worked on the RPi OS (Debian-based)

.. note::

  These lists are not exhaustive, only the most important attributes and
  functions are mentionned. See the `API reference`_ for more info.

0.0.1a0 (Aug 14, 2020)
======================
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

0.0.0a0 (Aug 9, 2020)
=====================
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
.. _LED symbols: #default-led-symbols-label
.. _API reference: api_reference.html
