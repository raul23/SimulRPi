=========
Changelog
=========

.. contents::
   :depth: 2
   :local:

Version 0.1.0a1
===============

**September 20, 2020**

* Remove *Work-In-Progress* from documentation
* Version 0.1.0a0.post1 was yanked for a clearer version number

Version 0.1.0a0
===============

**September 15, 2020**

.. _default-led-symbols-label:

* The default LED symbols are now big non-ASCII signs::

   🛑 : LED turned ON
   ⚪ : LED turned OFF

  **NOTE:** the default symbols used by all GPIO channels can be modified with
  :meth:`SimulRPi.GPIO.setdefaultsymbols`

* LED symbols for each channel can be modified with
  :meth:`SimulRPi.GPIO.setsymbols`
* Channel names can now be displayed instead of channel numbers in the terminal::

   🛑  [LED 1]        🛑  [LED 2]        🛑  [LED 3]        ⬤  [lightsaber]


* New modules: :mod:`SimulRPi.manager` and :mod:`SimulRPi.pindb`

  * :class:`~SimulRPi.manager.Manager` is now in its own module:
    :mod:`SimulRPi.manager`
  * :class:`~SimulRPi.pindb.Pin` and :class:`~SimulRPi.pindb.PinDB` are now in
    their own module: :mod:`SimulRPi.pindb`

  **NOTE:** these classes used to be in :mod:`SimulRPi.GPIO`

* New attributes in :class:`SimulRPi.pindb.Pin` and
  :class:`SimulRPi.manager.Manager`:

  * ``Pin.channel_id``: unique identifier
  * ``Pin.channel_name``: displayed in the terminal along each LED symbol
  * ``Pin.channel_number``: used to be called ``channel``
  * ``Pin.channel_type``: used to be called ``gpio_function``
    and refers to the type of GPIO channel, e.g. 1 (`GPIO.IN`) or 0
    (`GPIO.OUT`).
  * ``Pin.led_symbols``: each pin (aka channel) is represented by LED symbols
    if it is an output channel
  * ``Manager.default_led_symbols``: defines the `default LED symbols`_ used to
    represent each GPIO channel in the terminal

* New functions in :mod:`SimulRPi.GPIO`:

  * :meth:`~SimulRPi.GPIO.setchannelnames`: sets channels names for multiple
    channels
  * :meth:`~SimulRPi.GPIO.setchannels`: sets the attributes (e.g.
    ``channel_name`` and ``led_symbols``) for multiple channels
  * :meth:`~SimulRPi.GPIO.setdefaultsymbols`: changes the default LED symbols
    used by all output channels
  * :meth:`~SimulRPi.GPIO.setsymbols`: sets the LED symbols for multiple
    channels
  * :meth:`~SimulRPi.GPIO.wait`: waits for the threads to do their tasks and
    raises an exception if there was an error in a thread's target function.
    Hence, the main program can catch these thread exceptions.

* :meth:`SimulRPi.GPIO.output` accepts `channel` and `state` as :obj:`int`,
  :obj:`list` or :obj:`tuple`

* :meth:`SimulRPi.GPIO.setup` accepts `channel` as :obj:`int`, :obj:`list` or
  :obj:`tuple`

* The displaying thread in :mod:`SimulRPi.manager` is now an instance of
  :class:`~SimulRPi.manager.DisplayExceptionThread`. Thus, if there is an
  exception raised in :meth:`~SimulRPi.manager.Manager.display_leds()`, it is
  now possible to catch it in the main program

* The keyboard listener thread in :mod:`SimulRPi.manager`  is now an instance
  of ``KeyboardExceptionThread`` (a subclass of
  :class:`pynput.keyboard.Listener`). Thus, if there is an exception raised in
  :meth:`~SimulRPi.manager.Manager.on_press` or
  :meth:`~SimulRPi.manager.Manager.on_release`, it is now possible to catch it
  in the main program

* :meth:`SimulRPi.GPIO.input` and :meth:`SimulRPi.GPIO.output` now raise an
  exception caught by the listening and displaying threads, respectively.

* If two channels use the same channel numbers, an exception is now raised.

* :mod:`SimulRPi.run_examples`:

  * accepts the new option ``-a`` which will make use of ASCII-based LED
    symbols in case that you are having problems displaying the
    `default LED symbols`_ which use special characters (based on the **UTF-8**
    encoding). See `Display problems`_.
  * all simulation-based examples involving "LEDs" and pressing keyboard keys
    worked on the RPi OS (Debian-based)

.. seealso::

  The `SimulRPi API reference`_.

Version 0.0.1a0
===============

**August 14, 2020**

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

Version 0.0.0a0
===============

**August 9, 2020**

* Initial release

* Tested `code examples`_ on different platforms and here are the results

  * On an RPi with ``RPi.GPIO``: all examples involving LEDs and pressing
    buttons worked

  * On a computer with ``SimulRPi.GPIO``

    * macOS: all examples involving "LEDs" and keyboard keys worked
    * RPi OS [Debian-based]: all examples involving "LEDs" only worked

      **NOTE:** I was running the script :mod:`~SimulRPi.run_examples`
      with ``ssh`` but ``pynput`` doesn't detect any pressed keyboard key
      even though I set my environment variable ``Display``, added
      ``PYTHONPATH`` to *etc/sudoers* and ran the script with ``sudo``. To be
      further investigated.

[*NOTE:* tested the code examples with :mod:`~SimulRPi.run_examples`]
[*EDIT:* use *Initial release*]

.. URLs

.. 1. External links
.. _Xlib.error.DisplayNameError: https://travis-ci.org/github/raul23/SimulRPi/builds/716458786#L235

.. 2. Internal links
.. _code examples: README_docs.html#examples-label
.. _default LED symbols: #default-led-symbols-label
.. _SimulRPi API reference: api_reference.html
.. _Display problems: display_problems.html#non-ascii-characters-can-t-be-displayed
