# -*- coding: utf-8 -*-
"""Module that partly fakes `RPi.GPIO`_ and simulates some I/O devices.

It simulates these I/O devices connected to a Raspberry Pi:

    - push buttons by listening to pressed keyboard keys and
    - LEDs by displaying red dots blinking in the terminal along with
      their GPIO channel number.

When a LED is turned on, it is shown as a red dot in the terminal. The
`pynput`_ package is used to monitor the keyboard for any pressed key.

.. TODO: also found in README_docs.rst

**Example: terminal output** ::

    ⬤ [9]   ⬤ [10]   🔴 [11]

.. highlight:: python

where each dot represents a LED and the number between brackets is the
associated GPIO channel number.

.. important::

    This library is not a Raspberry Pi emulator nor a complete mock-up of
    `RPi.GPIO`_, only the most important functions that I needed for my
    `Darth-Vader-RPi project`_ were added.

    If there is enough interest in this library, I will eventually mock more
    functions from `RPi.GPIO`_.

.. URLs
.. external links
.. _pynput: https://pynput.readthedocs.io/en/latest/index.html
.. _pynput reference: https://pynput.readthedocs.io/en/latest/keyboard.html#pynput.keyboard.Key
.. _Darth-Vader-RPi project: https://github.com/raul23/Darth-Vader-RPi
.. _RPi.GPIO: https://pypi.org/project/RPi.GPIO/
.. _RPi.GPIO wiki: https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
.. _SimulRPi: https://pypi.org/project/SimulRPi
.. _SimulRPi.GPIO: https://pypi.org/project/SimulRPi

.. internal links
.. _default_key_to_channel_map: api_reference.html#content-default-keymap-label
.. _here: display_problems.html#non-ascii-characters-can-t-be-displayed
.. _installed: README_docs.html#installation-instructions
.. _script's usage: #usage

"""
import logging
import os
import time
from logging import NullHandler

import SimulRPi.manager

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

RPI_INFO = {'P1_REVISION': 1}
RPI_REVISION = 1  # Deprecated
VERSION = 1

BOARD = 0
BCM = 1
HIGH = 1
LOW = 0
IN = 0
OUT = 1
PUD_UP = 1
PUD_DOWN = 0

MODES = {'BOARD': BOARD, 'BCM': BCM}
manager = SimulRPi.manager.Manager()


def cleanup():
    """Clean up any resources (e.g. GPIO channels).

    At the end of any program, it is good practice to clean up any resources
    you might have used. This is no different with `RPi.GPIO`_. By returning
    all channels you have used back to inputs with no pull up/down, you can
    avoid accidental damage to your RPi by shorting out the pins.
    [**Ref:** `RPi.GPIO wiki`_]

    Also, the two threads responsible for displaying LEDs in the terminal and
    listening for pressed/released keys are stopped.

    .. note::

        On an RPi, ``cleanup()`` will:

            * only clean up GPIO channels that your script has used
            * also clear the pin numbering system in use (`BOARD` or `BCM`)

        **Ref.:** `RPi.GPIO wiki`_

        When using the ``SimulRPi`` package, :meth:`cleanup` will:

            * stop the displaying thread ``Manager.th_display_leds``
            * stop the listening thread ``Manager.th_listener``
            * show the cursor again which was hidden in
              :meth:`~SimulRPi.manager.Manager.display_leds`
            * reset the ``GPIO.manager``'s attributes (an instance of
              :class:`~SimulRPi.manager.Manager`)

    """
    # NOTE: global since we are deleting it at the end
    global manager
    # Show cursor again
    # TODO: works on UNIX shell only, not Windows
    # TODO: space
    os.system("tput cnorm ")
    # Check if displaying thread is alive. If the user didn't setup any output
    # channels for LEDs, then the displaying thread was never started
    if manager.th_display_leds.is_alive():
        manager.th_display_leds.do_run = False
        manager.th_display_leds.join()
        logger.debug("Thread stopped: {}".format(manager.th_display_leds.name))
    # Check if listening thread is alive. If the user didn't setup any input
    # channels for buttons, then the listener thread was never started
    if manager.th_listener and manager.th_listener.is_alive():
        logger.debug("Stopping thread: {}".format(manager.th_listener.name))
        manager.th_listener.stop()
        logger.debug("Thread stopped: {}".format(manager.th_listener.name))
    # Reset Manager's attributes
    del manager
    manager = SimulRPi.manager.Manager()


def input(channel):
    """Read the value of a GPIO pin.

    The listening thread is also started if possible.

    Parameters
    ----------
    channel : int
        Input channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).

    Returns
    -------
    state : :obj:`int` or :obj:`None`
        If no :class:`~SimulRPi.pindb.Pin` could be retrieved based on the
        given channel number, then :obj:`None` is returned. Otherwise, the
        :class:`~SimulRPi.pindb.Pin`\'s state is returned: 1 (`HIGH`) or 0
        (`LOW`).

    Raises
    ------
    Exception
        If the listening thread caught an exception that occurred in
        :meth:`~SimulRPi.manager.Manager.on_press` or
        :meth:`~SimulRPi.manager.Manager.on_release`, the said exception will
        be raised here.


    .. note::

        The listening thread (for monitoring pressed keys) is started if there
        is no exception caught by the thread and if it is not alive, i.e. it is
        not already running.

    .. important::

        The reason for checking if there is no exception already caught by a
        thread, i.e. ``if not manager.th_listener.exc``, is to avoid having
        another thread calling this function and re-starting the failed thread.
        Hence, we avoid raising a :exc:`RuntimeError` on top of the thread's
        already caught exception.

    """
    # Start the listening thread only if it is not already alive and there is no
    # exception in the thread's target function
    if manager.th_listener:
        if not manager.th_listener.exc and not manager.th_listener.is_alive():
            manager.th_listener.start()
        _raise_if_thread_exception(manager.th_listener.name)
    return manager.pin_db.get_pin_state(channel)


def output(channel, state):
    """Set the output state of a GPIO pin.

    The displaying thread is also started if possible.

    Parameters
    ----------
    channel : int or list or tuple
        Output channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).

        You can also provide a list or tuple of channel numbers::

            chan_list = [11,12]
    state : int or list or tuple
        State of the GPIO channel: 1 (`HIGH`) or 0 (`LOW`).

        You can also provide a list of states::

            chan_list = [11,12]
            GPIO.output(chan_list, GPIO.LOW)               # sets all to LOW
            GPIO.output(chan_list, (GPIO.HIGH, GPIO.LOW))  # sets 1st HIGH and 2nd LOW.

    Raises
    ------
    Exception
        If the displaying thread caught an exception that occurred in its
        target function :meth:`~SimulRPi.manager.Manager.display_leds`, the
        said exception will be raised here.


    .. note::

        The displaying thread (for showing "LEDs" on the terminal) is started
        if there is no exception caught by the thread and if it is not alive,
        i.e. it is not already running.

    See Also
    --------
    :meth:`input`: Read the **Important** message about why we need to check if
                   there is an exception caught by the thread when trying to
                   start it.

    """
    channel = [channel] if isinstance(channel, int) else channel
    state = [state] if isinstance(state, int) else state
    if len(channel) > 1:
        if len(state) == 1:
            state = state * len(channel)
        else:
            assert len(state) == len(channel), \
                "There should be as many output states as channels: " \
                "states = {} and channels = {}".format(state, channel)
    for idx, ch in enumerate(channel):
        manager.pin_db.set_pin_state_from_channel(ch, state[idx])
    # Start the displaying thread only if it is not already alive and there is
    # no exception in the thread's target function
    if not manager.th_display_leds.exc and \
            not manager.th_display_leds.is_alive():
        manager.th_display_leds.start()
    _raise_if_thread_exception(manager.th_display_leds.name)


def setchannelnames(channel_names):
    """Set the channel names for multiple channels

    The channel names will be displayed in the terminal along each LED symbol.
    If no channel name is given, then the channel number will be shown.

    Parameters
    ----------
    channel_names : dict
        Dictionary that maps channel numbers (:obj:`int`) to channel names
        (:obj:`str`).

        **Example**::

            channel_names = {
                1: "The Channel 1",
                2: "The Channel 2"
            }

    """
    manager.update_channel_names(channel_names)


def setchannels(gpio_channels):
    """Set the attributes (e.g. `channel_name` and `led_symbols`) for multiple
    channels.

    The attributes that can be updated for a given GPIO channel are:

        * ``channel_id``: unique identifier
        * ``channel_name``: will be shown along the LED symbol in the terminal
        * ``channel_number``: GPIO channel number based on the numbering system
          you have specified (`BOARD` or `BCM`).
        * ``led_symbols``: should only be defined for output channels. It is a
          dictionary defining the symbols to be used when the LED is turned ON
          and OFF.
        * ``key``: keyboard key associated with a channel, e.g. "*cmd_r*".

    Parameters
    ----------
    gpio_channels : list
        A list where each item is a dictionary defining the attributes for a
        given GPIO channel.

        **Example**::

            gpio_channels = [
                {
                    "channel_id": "lightsaber_button",
                    "channel_name": "lightsaber_button",
                    "channel_number": 23,
                    "key": "cmd"
                },
                {
                    "channel_id": "lightsaber_led",
                    "channel_name": "lightsaber",
                    "channel_number": 22,
                    "led_symbols": {
                        "ON": "\\033[1;31;48m⬤\\033[1;37;0m",
                        "OFF": "⬤"
                    }
                }
            ]

    Raises
    ------
    KeyError
        Raised if two channels are using the same channel number.

    """
    channels_attributes = {}
    key_maps = {}
    for gpio_ch in gpio_channels:
        channel_id = gpio_ch['channel_id']
        channel_name = gpio_ch.get('channel_name')
        channel_number = int(gpio_ch.get('channel_number'))
        led_symbols = gpio_ch.get('led_symbols')
        if channel_number in channels_attributes:
            # TODO: error or warning? Overwrite?
            raise KeyError("The channel '{}' is using a channel number {} "
                           "that is already taken by the channel '{}'".format(
                            channel_id,
                            channel_number,
                            channels_attributes[channel_number]['channel_id']))
        else:
            channels_attributes.setdefault(channel_number, {})
            channels_attributes[channel_number] = {
                'channel_id': channel_id,
                'channel_name': channel_name,
                'led_symbols': led_symbols
            }
        if gpio_ch.get('key'):
            key_maps.update({gpio_ch.get('key'): channel_number})
    manager.bulk_channel_update(channels_attributes)
    setkeymap(key_maps)


def setdefaultsymbols(default_led_symbols):
    """Set the default LED symbols used by all output channels.

    Parameters
    ----------
    default_led_symbols : str or dict
        Dictionary that maps each output state (:obj:`str`, {'`ON`',
        '`OFF`'}) to the LED symbol (:obj:`str`).

        **Example**::

            default_led_symbols = {
                'ON': '🔵',
                'OFF': '⚪ '
            }

        You can also provide the string ``default_ascii`` to make use of
        ASCII-based LED symbols for all output channels. Useful if you are
        still having problems displaying the default LED signs (which make use
        of special characters) after you have tried the solutions shown
        `here`_::

            default_led_symbols = "default_ascii"

    """
    manager.update_default_led_symbols(default_led_symbols)


# TODO: explain that the mapping is unique in both ways, i.e. one keyboard key
# can only be associated to a one GPIO channel, and vice versa.
def setkeymap(key_to_channel_map):
    """Set the default keymap dictionary with new keys and channels.

    The default dictionary `default_key_to_channel_map`_ that maps keyboard
    keys to GPIO channels can be modified by providing your own mapping
    ``key_to_channel_map`` containing only the keys and channels that you
    want to be modified.

    Parameters
    ----------
    key_to_channel_map : dict
        A dictionary mapping keys (:obj:`str`) to GPIO channel numbers
        (:obj:`int`) that will be used to update the default keymap.

        **For example**::

            key_to_channel_map = {
                "q": 23,
                "w": 24,
                "e": 25
            }

    """
    manager.update_keymap(key_to_channel_map)


def setmode(mode):
    """Set the numbering system used to identify the I/O pins on an RPi within
    ``RPi.GPIO``.

    There are two ways of numbering the I/O pins on a Raspberry Pi within
    ``RPi.GPIO``:

    1. The `BOARD` numbering system: refers to the pin numbers on the P1 header
       of the Raspberry Pi board
    2. The `BCM` numbers: refers to the channel numbers on the Broadcom SOC.

    Parameters
    ----------
    mode : int
        Numbering system used to identify the I/O pins on an RPi: `BOARD` or
        `BCM`.

    References
    ----------
    Function description and more info from `RPi.GPIO wiki`_.

    """
    assert mode in MODES.values(), \
        "Wrong mode: {}. Mode should be one these values: {}".format(
            mode, list(MODES.values()))
    manager.mode = mode


def setprinting(enable_printing):
    """Enable or disable printing to the terminal.

    If printing is enabled, blinking red dots will be shown in the terminal,
    simulating LEDs connected to a Raspberry Pi. Otherwise, nothing will be
    printed in the terminal.

    Parameters
    ----------
    enable_printing : bool
        If `True`. printing to the terminal is enabled. Otherwise, printing
        will be disabled.

    """
    # TODO: stop displaying thread too?
    manager.enable_printing = enable_printing


def setsymbols(led_symbols):
    """Set the LED symbols for multiple output channels.

    Parameters
    ----------
    led_symbols : dict
        Dictionary that maps channel numbers (:obj:`int`) to LED symbols
        (:obj:`dict`).

        **Example**::

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

    """
    manager.update_led_symbols(led_symbols)


def setup(channel, channel_type, pull_up_down=None, initial=None):
    """Setup a GPIO channel as an input or output.

    To configure a channel as an input::

        GPIO.setup(channel, GPIO.IN)

    To configure a channel as an output::

        GPIO.setup(channel, GPIO.OUT)

    You can also specify an initial value for your output channel::

        GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)

    Parameters
    ----------
    channel : int or list or tuple
        GPIO channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).

        You can also provide a list or tuple of channel numbers. All channels
        will take the same values for the other parameters.
    channel_type : int
        Type of a GPIO channel: e.g. 1 (`GPIO.IN`) or 0 (`GPIO.OUT`).
    pull_up_down : int or None, optional
        Initial value of an input channel, e.g. `GPIO.PUP_UP`. Default value is
        :obj:`None`.
    initial : int or None, optional
        Initial value of an output channel, e.g. `GPIO.HIGH`. Default value is
        :obj:`None`.

    References
    ----------
    `RPi.GPIO wiki`_

    """
    channel = [channel] if isinstance(channel, int) else channel
    for ch in channel:
        manager.add_pin(ch, channel_type, pull_up_down, initial)


def setwarnings(show_warnings):
    """Set warnings when configuring a GPIO pin other than the default
    (input).

    It is possible that you have more than one script/circuit on the GPIO of
    your Raspberry Pi. As a result of this, if ``RPi.GPIO`` detects that a pin
    has been configured to something other than the default (input), you get a
    warning when you try to configure a script. [**Ref:** `RPi.GPIO wiki`_]

    Parameters
    ----------
    show_warnings : bool
        Whether to show warnings when using a pin other than the default GPIO
        function (input).

    """
    manager.warnings = show_warnings


def wait(timeout=2):
    """Wait for certain events to complete.

    Wait for the displaying and listening threads to do their tasks. If there
    was an exception caught and saved by one thread, then it is raised here.

    If more than ``timeout`` seconds elapsed without any of the events
    described previously happening, the function exits.

    Parameters
    ----------
    timeout : float
        How long to wait (in seconds) before exiting from this function. By
        default, we wait for 2 seconds.

    Raises
    ------
    Exception
        If the displaying or listening thread caught an exception, it will be
        raised here.


    .. important::

        This function is not called in :meth:`cleanup` because if a thread
        exception is raised, it will not be caught in the main program because
        :meth:`cleanup` should be found in a ``finally`` block:

        .. code-block:: python
           :emphasize-lines: 8

           try:
               do_something_with_gpio_api()
               GPIO.wait()
           except Exception as e:
               # Do something with error
               print(e)
           finally:
               GPIO.cleanup()

    """
    # logger.debug("Waiting after threads...")
    start = time.time()
    while True:
        if not manager.th_display_leds.is_alive() or \
                (manager.th_listener and not manager.th_listener.is_alive()):
            _raise_if_thread_exception('all')
        if (time.time() - start) > timeout:
            break
    # logger.debug("Good, no thread exception raised!")


def _raise_if_thread_exception(which_threads):
    """TODO

    Parameters
    ----------
    which_threads : str

    Raises
    -------

    """
    if which_threads in [manager.th_display_leds.name, 'all']:
        if manager.th_display_leds.exc and \
                not manager.th_display_leds.exception_raised:
            # Happens when error in Manager.display_leds()
            manager.th_display_leds.exception_raised = True
            raise manager.th_display_leds.exc
    if manager.th_listener and which_threads in [manager.th_listener.name, 'all']:
        if manager.th_listener.exc and not manager.th_listener.exception_raised:
            # Happens when error in Manager.on_press() and/or Manager.on_release()
            manager.th_listener.exception_raised = True
            raise manager.th_listener.exc
