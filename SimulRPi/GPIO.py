# -*- coding: utf-8 -*-
"""Module that partly fakes `RPi.GPIO`_ and simulates some I/O devices.

It simulates these I/O devices connected to a Raspberry Pi:

    - push buttons by listening to pressed keyboard keys and
    - LEDs by displaying red dots blinking in the terminal along with
      their GPIO channel number.

When a LED is turned on, it is shown as a red dot in the terminal. The
package `pynput`_ is used to monitor the keyboard for any pressed key.

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
    functions from `RPi.GPIO`_. Thus,
    let me know through `SimulRPi's issues page`_ if you want me to add more
    things to this library.

.. TODO: also found in README_docs.rst
.. TODO: IMPORTANT check URL to config file

.. URLs
.. external links
.. _here: https://github.com/raul23/Darth-Vader-RPi/blob/master/darth_vader_rpi/configs/default_main_cfg.json#L11
.. _pynput: https://pynput.readthedocs.io/en/latest/index.html
.. _Darth-Vader-RPi project: https://github.com/raul23/Darth-Vader-RPi
.. _RPi.GPIO: https://pypi.org/project/RPi.GPIO/
.. _RPi.GPIO wiki: https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
.. _SimulRPi's issues page: https://github.com/raul23/SimulRPi/issues

.. internal links
.. _default_key_to_channel_map: api_reference.html#content-default-keymap-label

"""
import copy
import logging
import os
import threading
import time
from logging import NullHandler

try:
    from pynput import keyboard
except ImportError:
    print("`pynput` couldn't be found. Thus, no keyboard keys will be detected "
          "if pressed or released.\nIf you need this option, install `pynput` "
          "with: pip install pynput.\n")
    keyboard = None

from SimulRPi.mapping import default_key_to_channel_map

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
CHANNEL_TYPES = {IN: 'INPUT', OUT: 'OUTPUT'}


class ExceptionThread(threading.Thread):
    """A subclass from :class:`threading.Thread` that defines threads that can
    catch errors if their target functions raise an exception.

    Attributes
    ----------
    exception_raised : bool
        When the exception is raised, it should be set to `True`. By default, it
        is `False`.
    exc: :class:`Exception`
        Represent the exception raised by the target function.

    References
    ----------
    * `stackoverflow <https://stackoverflow.com/a/51270466>`__

    """

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.exception_raised = False
        self.exc = None

    def run(self):
        """Method representing the thread’s activity.

        Overridden from the base class :class:`threading.Thread`. This method
        invokes the callable object passed to the object’s constructor as the
        target argument, if any, with sequential and keyword arguments taken
        from the args and kwargs arguments, respectively.

        It also saves any error that the target function might raise.

        .. important::

            The exception is only caught here, not raised. The exception is
            further raised in :meth:`output`. The reason for not raising it
            here is to avoid having another thread re-starting the failed
            thread by calling :meth:`output` while the main program is busy
            catching the exception. Hence, we avoid raising a
            :exc:`RuntimeError` on top of the thread's caught exception.

        """
        try:
            self._target(*self._args, **self._kwargs)
        except Exception as e:
            # TODO: important add a method to raise the exception
            self.exc = e


if keyboard:
    class KeyboardExceptionThread(keyboard.Listener):
        """A subclass from :class:`pynput.keyboard.Listener` that defines
        threads that store the exception raised in their target function.

        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.exception_raised = False
            self.exc = None


# TODO: change to Channel?
class Pin:
    """Class that represents a GPIO pin.

    Parameters
    ----------
    channel_number : int
        GPIO channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).
    channel_id : str
        Unique identifier.
    gpio_type : int
        Type of a GPIO channel: e.g. 1 (`GPIO.IN`) or 0 (`GPIO.OUT`).
    channel_name : str, optional
        It will be displayed in the terminal along with the LED symbol if it is
        available. Otherwise, the ``channel_number`` is shown. By default, its
        value is :obj:`None`.
    key : str or None, optional
        Keyboard key associated with the GPIO channel, e.g. `cmd_r`.
    led_symbols : dict, optional
        It should only be defined for output channels. It is a dictionary
        defining the symbols to be used when the LED is turned ON and OFF. If
        not found for an ouput channel, then the default LED symbols will be
        used as specified in :class:`Manager`.

        **Example**::

            {
                "ON": "🔵",
                "OFF": "⚪ "
            }

    pull_up_down : int or None, optional
        Initial value of an input channel, e.g. `GPIO.PUP_UP`. Default value is
        :obj:`None`.
    initial : int or None, optional
        Initial value of an output channel, e.g. `GPIO.HIGH`. Default value is
        :obj:`None`.

    Attributes
    ----------
    state : int
        State of the GPIO channel: 1 (`HIGH`) or 0 (`LOW`).

    """
    def __init__(self, channel_number, channel_id, channel_type,
                 channel_name=None, key=None, led_symbols=None,
                 pull_up_down=None, initial=None):
        self.channel_number = channel_number
        self.channel_id = channel_id
        self.channel_type = channel_type
        self.channel_name = channel_name
        self.key = key
        self.pull_up_down = pull_up_down
        self.initial = initial
        self.led_symbols = led_symbols
        # TODO: check if setting of state is good
        if self.channel_type == IN:
            # Input channel (e.g. push button)
            self.state = self.initial if self.initial else HIGH
        else:
            # Output channel (e.g. LED)
            self.state = self.initial if self.initial else LOW


# TODO: change to ChannelDB?
# TODO: add
class PinDB:
    """Class for storing and modifying :class:`Pin`\s.

    Each instance of :class:`Pin` is saved in a dictionary that maps it
    to its channel number.

    .. note::

        The dictionary (a "database" of :class:`Pin`\s) must be accessed
        through the different methods available in :class:`PinDB`, e.g.
        :meth:`get_pin_from_channel`.

    """
    def __init__(self):
        # Maps channel to Pin object
        self._pins = {}
        # TODO: explain more
        # Maps keyboard key to Pin object
        # NOTE: this dict is only for INPUT channels with an associated key
        self._key_to_pin_map = {}
        # List only for OUTPUT channels
        self.output_pins = []

    def create_pin(self, channel_number, channel_id, channel_type, **kwargs):
        """Create an instance of :class:`Pin` and save it in a dictionary.

        Based on the given arguments, an instance of :class:`Pin` is
        created and added to a dictionary that acts like a database of pins
        with the key being the pin's channel number and the value is an
        instance of :class:`Pin`.

        Parameters
        ----------
        channel_number : int
            GPIO channel number based on the numbering system you have specified
            (`BOARD` or `BCM`).
        channel_id : str
            Unique identifier.
        channel_type : int
            Type of a GPIO channel: e.g. 1 (`GPIO.IN`) or 0 (`GPIO.OUT`).
        kwargs : dict, optional
            These are the (optional) keyword arguments for ``Pin.__init__()``.
            See :class:`Pin` for a list of its parameters which can be included
            in ``kwargs``.

        Raises
        ------
        KeyError
            Raised if two channels are using the same channel number.

        """
        if self._pins.get(channel_number):
            # TODO: error or warning? Overwrite?
            raise KeyError("Duplicate channel numbers: {}".format(channel_number))
        self._pins[channel_number] = Pin(channel_number, channel_id,
                                         channel_type, **kwargs)
        if channel_type == OUT:
            # Output channel (e.g. LED)
            # Save the output pin so the thread that displays LEDs knows what
            # pins are OUTPUT and therefore connected to LEDs.
            self.output_pins.append(self._pins[channel_number])
        # Update the other internal dict if key is given
        if kwargs['key']:
            # Input channel (e.g. push button)
            # TODO: assert on channel_type which should be IN?
            self._key_to_pin_map[kwargs['key']] = self._pins[channel_number]

    def get_pin_from_channel(self, channel_number):
        """Get a :class:`Pin` from a given channel.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` to be
            retrieved.

        Returns
        -------
        Pin : :class:`Pin` or :obj:`None`
            If no :class:`Pin` could be retrieved based on the given channel,
            :obj:`None` is returned. Otherwise, a :class:`Pin` object is
            returned.

        """
        return self._pins.get(channel_number)

    def get_pin_from_key(self, key):
        """Get a :class:`Pin` from a given pressed/released key.

        Parameters
        ----------
        key : str
            The pressed/released key that is associated with the :class:`Pin`
            to be retrieved.

        Returns
        -------
        Pin : :class:`Pin` or :obj:`None`
            If no :class:`Pin` could be retrieved based on the given key,
            :obj:`None` is returned. Otherwise, a :class:`Pin` object is
            returned.

        """
        return self._key_to_pin_map.get(key)

    def get_pin_state(self, channel_number):
        """Get a :class:`Pin`\'s state from a given channel.

        The state associated with a :class:`Pin` can either be 1 (`HIGH`) or 0
        (`LOW`).

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` whose state is
            to be returned.

        Returns
        -------
        state : :obj:`int` or :obj:`None`
            If no :class:`Pin` could be retrieved based on the given channel
            number, then :obj:`None` is returned. Otherwise, the
            :class:`Pin`\'s state is returned: 1 (`HIGH`) or 0 (`LOW`).

        """
        pin = self._pins.get(channel_number)
        if pin:
            return pin.state
        else:
            return None

    def set_pin_key_from_channel(self, channel_number, key):
        """Set a :class:`Pin`\'s key from a given channel.

        A :class:`Pin` is retrieved based on a given channel, then its
        ``key`` is set with `key`.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` whose key will
            be set.
        key : str
            The new keyboard key that a :class:`Pin` will be updated with.

        Returns
        -------
        retval : bool
            Returns `True` if the :class:`Pin` was successfully set with `key`.
            Otherwise, it returns `False`.

        """
        pin = self.get_pin_from_channel(channel_number)
        if pin:
            old_key = pin.key
            pin.key = key
            # TODO: only update dict if the key is different from the actual
            # pin's key but then return True or False if no update?
            # if key != old_key:
            del self._key_to_pin_map[old_key]
            self._key_to_pin_map[key] = pin
            return True
        else:
            return False

    def set_pin_name_from_channel(self, channel_number, channel_name):
        """Set a :class:`Pin`\'s channel name from a given channel number.

        A :class:`Pin` is retrieved based on a given channel, then its
        ``channel_name`` is set with `channel_name`.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` whose channel
            name will be set.
        channel_name : str
            The new channel name that a :class:`Pin` will be updated with.

        Returns
        -------
        retval : bool
            Returns `True` if the :class:`Pin` was successfully set with
            `channel_name`. Otherwise, it returns `False`.

        """
        pin = self.get_pin_from_channel(channel_number)
        if pin:
            # TODO: only update name if the name is different from the actual
            pin.channel_name = channel_name
            return True
        else:
            return False

    def set_pin_id_from_channel(self, channel_number, channel_id):
        """Set a :class:`Pin`\'s channel id from a given channel number.

        A :class:`Pin` is retrieved based on a given channel, then its
        ``channel_id`` is set with `channel_id`.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` whose channel
            id will be set.
        channel_id : str
            The new channel id that a :class:`Pin` will be updated with.

        Returns
        -------
        retval : bool
            Returns `True` if the :class:`Pin` was successfully set with
            `channel_id`. Otherwise, it returns `False`.

        """
        pin = self.get_pin_from_channel(channel_number)
        if pin:
            # TODO: only update id if the id is different from the actual
            pin.channel_id = channel_id
            return True
        else:
            return False

    def set_pin_state_from_channel(self, channel_number, state):
        """Set a :class:`Pin`\'s state from a given channel.

        A :class:`Pin` is retrieved based on a given channel, then its
        ``state`` is set with `state`.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` whose state
            will be set.
        state : int
            State the GPIO channel should take: 1 (`HIGH`) or 0 (`LOW`).
        Returns
        -------
        retval : bool
            Returns `True` if the :class:`Pin` was successfully set with
            `state`. Otherwise, it returns `False`.

        """
        pin = self.get_pin_from_channel(channel_number)
        if pin:
            # TODO: only update state if the state is different from the actual
            pin.state = state
            return True
        else:
            return False

    def set_pin_state_from_key(self, key, state):
        """Set a :class:`Pin`\'s state from a given key.

        A :class:`Pin` is retrieved based on a given key, then its
        ``state`` is set with `state`.

        Parameters
        ----------
        key : str
            The keyboard key associated with the :class:`Pin` whose state will
            be set.
        state : int
            State the GPIO channel should take: 1 (`HIGH`) or 0 (`LOW`).
        Returns
        -------
        retval : bool
            Returns `True` if the :class:`Pin` was successfully set with
            `state`. Otherwise, it returns `False`.

        """
        pin = self.get_pin_from_key(key)
        if pin:
            # TODO: only update state if the state is different from the actual
            pin.state = state
            return True
        else:
            return False

    def set_pin_symbols_from_channel(self, channel_number, led_symbols):
        """Set a :class:`Pin`\'s led symbols from a given channel.

        A :class:`Pin` is retrieved based on a given key, then its
        ``state`` is set with `state`.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` whose state
            will be set.
        led_symbols : dict
            It is a dictionary defining the symbols to be used when the LED is
            turned ON and OFF. See :class:`Pin` for more info about this
            attribute.
        Returns
        -------
        retval : bool
            Returns `True` if the :class:`Pin` was successfully set with
            `led_symbols`. Otherwise, it returns `False`.

        """
        pin = self.get_pin_from_channel(channel_number)
        if pin:
            # TODO: only update symbols if the symbols is different from the actual
            pin.led_symbols = led_symbols
            return True
        else:
            return False


class Manager:
    """Class that manages the pin database (:class:`PinDB`) and the threads
    responsible for displaying "LEDs" on the terminal and listening for keys
    pressed/released.

    The threads are not started right away in ``__init__()`` but in
    :meth:`input` for the listener thread and :meth:`output` for the displaying
    thread.

    They are eventually stopped in :meth:`cleanup`.

    Attributes
    ----------
    mode : int
        Numbering system used to identify the I/O pins on an RPi: `BOARD` or
        `BCM`.  Default value is :obj:`None`.
    warnings : bool
        Whether to show warnings when using a pin other than the default GPIO
        function (input). Default value is `True`.
    enable_printing : bool
        Whether to enable printing on the terminal. Default value is `True`.
    pin_db : PinDB
        A database of :class:`Pin`\s. See :class:`PinDB` on how to access it.
    default_led_symbols : dict
        A dictionary that maps each output channel's state ('ON' and 'OFF') to
        a LED symbol. By default, it is set to these LED symbols::

            default_led_symbols = {
                "ON": "🛑",
                "OFF": "⚪"
            }
    key_to_channel_map : dict
        A dictionary that maps keyboard keys (:obj:`string`) to GPIO channel
        numbers (:obj:`int`). By default, it takes the keys and values defined
        in the keymap `default_key_to_channel_map`_.
    channel_to_key_map : dict
        The reverse dictionary of ``key_to_channel_map``. It maps channels to
        keys.
    th_display_leds : GPIO.ExceptionThread
        Thread responsible for displaying blinking red dots in the terminal as
        to simulate LEDs connected to an RPi.
    th_listener : GPIO.KeyboardExceptionThread
        Thread responsible for listening on any pressed or released keyboard
        key as to simulate push buttons connected to an RPi.

        If ``pynput`` couldn't be imported, ``th_listener`` is :obj:`None`.
        Otherwise, it is instantiated from ``GPIO.KeyboardExceptionThread``.

        .. note::

            A keyboard listener is a subclass of :class:`threading.Thread`, and
            all callbacks will be invoked from the thread.

            **Ref.:** https://pynput.readthedocs.io/en/latest/keyboard.html#monitoring-the-keyboard


    .. important::

        If the module ``pynput.keyboard`` couldn't be imported, the listener
        thread ``th_listener`` will not be created and the parts of the
        ``SimulRPi`` library that monitors the keyboard for any pressed or
        released key will be ignored. Only the thread ``th_display_leds`` that
        displays "LEDs" on the terminal will be created.

        This is necessary for example in the case we are running tests on
        travis and we don't want travis to install ``pynput`` in a headless
        setup because the following exception will get raised::

            Xlib.error.DisplayNameError: Bad display name ""

        The tests involving ``pynput`` will be performed with a mock version of
        ``pynput``.

    """
    def __init__(self):
        self.mode = None
        self.warnings = True
        self.enable_printing = True
        self.pin_db = PinDB()
        self.default_led_symbols = {
            "ON": "\U0001F6D1",
            "OFF": "\U000026AA"
        }
        # TODO: call it _channel_cached_info?
        self._channel_tmp_info = {}
        self.key_to_channel_map = copy.copy(default_key_to_channel_map)
        self.channel_to_key_map = {v: k for k, v in
                                   self.key_to_channel_map.items()}
        self.th_display_leds = ExceptionThread(name="thread_display_leds",
                                               target=self.display_leds,
                                               args=())
        if keyboard:
            self.th_listener = KeyboardExceptionThread(
                on_press=self.on_press,
                on_release=self.on_release)
            self.th_listener.name = "thread_listener"
        else:
            self.th_listener = None

    def add_pin(self, channel_number, channel_type, pull_up_down=None, initial=None):
        """Add an input or output pin to the pin database.

        An instance of :class:`Pin` is created with the given arguments and
        added to the pin database :class:`PinDB`.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` to be added in
            the pin database.
        channel_type : int
            Type of a GPIO channel: e.g. 1 (`GPIO.IN`) or 0 (`GPIO.OUT`).
        pull_up_down : int or None, optional
            Initial value of an input channel, e.g. `GPIO.PUP_UP`. Default
            value is :obj:`None`.
        initial : int or None, optional
            Initial value of an output channel, e.g. `GPIO.HIGH`. Default value
            is :obj:`None`.

        """
        key = None
        tmp_info = self._channel_tmp_info.get(channel_number, {})
        if channel_type == IN:
            # Get keyboard key associated with the INPUT pin (button)
            # TODO: add key also in _channel_tmp_info?
            key = self.channel_to_key_map.get(channel_number)
            tmp_info['led_symbols'] = None
        if self._channel_tmp_info.get(channel_number):
            del self._channel_tmp_info[channel_number]
        self.pin_db.create_pin(
            channel_number=channel_number,
            channel_id=tmp_info.get('channel_id', channel_number),
            channel_type=channel_type,
            channel_name=tmp_info.get('channel_name', channel_number),
            key=key,
            led_symbols=tmp_info.get('led_symbols', self.default_led_symbols),
            pull_up_down=pull_up_down,
            initial=initial)

    def bulk_channel_update(self, new_channels_attributes):
        """Update the attributes (e.g. `channel_name` and `led_symbols`) for
        multiple channels.

        If a channel number is associated with a not yet created :class:`Pin`,
        the corresponding attributes will be temporary saved for later when the
        pin object will be created with :meth:`add_pin`.

        Parameters
        ----------
        new_channels_attributes : dict
            A dictionary mapping channel numbers (:obj:`int`) with channels'
            attributes (:obj:`dict`). The accepted attributes are those
            specified in :meth:`setchannels`.

            **Example**::

                new_channels_attributes = {
                    1: {
                        'channel_id': 'channel1',
                        'channel_name': 'The Channel 1',
                        'led_symbols': {
                            'ON': '🔵',
                            'OFF': '⚪ '
                        }
                    }.
                    2: {
                        'channel_id': 'channel2',
                        'channel_name': 'The Channel 2',
                        'key': 'cmd_r'
                    }
                }

        """
        for ch_number, ch_attributes in new_channels_attributes.items():
            for attribute_name, attribute_value in ch_attributes.items():
                self._update_attribute_pins(
                    attribute_name,
                    {ch_number: attribute_value})

    def display_leds(self):
        """Simulate LEDs connected to an RPi by blinking red dots in a terminal.

        In order to simulate LEDs turning on/off on an RPi, red dots are blinked
        in the terminal along with their GPIO channel number.

        When a LED is turned on, it is shown as a red dot in the terminal.

        .. highlight:: none

        **Example: terminal output** ::

            ⬤ [9]   ⬤ [10]   🔴 [11]

        .. highlight:: python

        where each dot represents a LED and the number between brackets is the
        associated GPIO channel number.

        This is the target function for the displaying thread ``th_display_leds``.

        .. note::

            If ``enable_printing`` is set to `True`, the terminal's cursor will
            be hidden. It will be eventually shown again in :meth:`cleanup`
            which is called by the main program when it is exiting.

            The reason is to avoid messing with the display of LEDs done by the
            displaying thread ``th_display_leds``.

        .. note::

            Since the displaying thread ``th_display_leds`` is an
            :class:`ExceptionThread` object, it has an attribute ``exc`` which
            stores the exception raised by this target function.

        .. important::

            :meth:`display_leds` should be run by a thread and eventually
            stopped from the main thread by setting its ``do_run`` attribute to
            `False` to let the thread exit from its target function.

            **For example**:

            .. code-block:: python

                th = ExceptionThread(target=self.display_leds, args=())
                th.start()

                # Your other code ...

                # Time to stop thread
                th.do_run = False
                th.join()

        """
        # TODO: explain order outputs are setup is how the channels are shown
        if self.enable_printing:
            # Hide the cursor
            # TODO: works on UNIX shell only, not Windows
            os.system("tput civis")
            print()
        th = threading.currentThread()
        # TODO: reduce number of prints, i.e. computations
        while getattr(th, "do_run", True):
            leds = ""
            last_msg_length = len(leds) if leds else 0
            # test = 1/0
            # for channel in sorted(self.channel_output_state_map):
            for pin in self.pin_db.output_pins:
                channel = pin.channel_number
                # TODO: pin could be None
                if pin.state == HIGH:
                    # Turn ON LED
                    # TODO: safeguard?
                    led_symbol = pin.led_symbols.get(
                        'ON', self.default_led_symbols['ON'])
                else:
                    # Turn OFF LED
                    # TODO: safeguard?
                    led_symbol = pin.led_symbols.get(
                        'OFF', self.default_led_symbols['OFF'])
                channel = pin.channel_name if pin.channel_name else channel
                leds += "{led_symbol}{spaces1}[{channel}]{spaces2}".format(
                    spaces1="  ",
                    led_symbol=led_symbol,
                    channel=channel,
                    spaces2=" " * 8)
            if self.enable_printing:
                print(' ' * last_msg_length, end='\r')
                print('  {}'.format(leds), end='\r')
        if self.enable_printing:
            print('  {}'.format(leds))
        logger.debug("Stopping thread: {}".format(th.name))

    @staticmethod
    def get_key_name(key):
        """Get the name of a keyboard key as a string.

        The name of the special or alphanumeric key is given by the package
        `pynput`_.

        Parameters
        ----------
        key : pynput.keyboard.Key or pynput.keyboard.KeyCode
            The keyboard key (from ``pynput.keyboard``) whose name will be
            returned.

        Returns
        -------
        key_name : str or None
            Returns the name of the given keyboard key if one was found by
            `pynput`_. Otherwise, it returns :obj:`None`.

        """
        # TODO: how to detect enter key
        # print(key)
        if hasattr(key, 'char'):
            # Alphanumeric key (keyboard.KeyCode)
            if key.char == '\x05':
                key_name = "insert"
            elif key.char == '\x1b':
                key_name = "num_lock"
            else:
                key_name = key.char
        elif hasattr(key, 'name'):
            # Special key (keyboard.Key)
            key_name = key.name
        else:
            # Unknown key
            key_name = None
        return key_name

    def on_press(self, key):
        """When a valid keyboard key is pressed, set its state to `GPIO.LOW`.

        Callback invoked from the thread ``th_listener``.

        This thread is used to monitor the keyboard for any valid pressed key.
        Only keys defined in the pin database are treated, i.e. keys that were
        configured with :meth:`setup` are further processed.

        Once a valid key is detected as pressed, its state is changed to
        `GPIO.LOW`.

        Parameters
        ----------
        key : pynput.keyboard.Key, pynput.keyboard.KeyCode, or None
            The key parameter passed to callbacks is

            * a :class:`pynput.keyboard.Key` for special keys,
            * a :class:`pynput.keyboard.KeyCode` for normal alphanumeric keys, or
            * :obj:`None` for unknown keys.

            **Ref.:** https://bit.ly/3k4whEs


        .. note::

            If an exception is raised, it is caught to be further raised in
            :meth:`input` or :meth:`wait`.

        """
        try:
            # test = 1/0
            self.pin_db.set_pin_state_from_key(self.get_key_name(key), state=LOW)
        except Exception as e:
            self.th_listener.exc = e

    def on_release(self, key):
        """When a valid keyboard key is released, set its state to `GPIO.HIGH`.

        Callback invoked from the thread ``th_listener``.

        This thread is used to monitor the keyboard for any valid released key.
        Only keys defined in the pin database are treated, i.e. keys that were
        configured with :meth:`setup` are further processed.

        Once a valid key is detected as released, its state is changed to
        `GPIO.HIGH`.

        Parameters
        ----------
        key : pynput.keyboard.Key, pynput.keyboard.KeyCode, or None
            The key parameter passed to callbacks is

            * a :class:`pynput.keyboard.Key` for special keys,
            * a :class:`pynput.keyboard.KeyCode` for normal alphanumeric keys, or
            * :obj:`None` for unknown keys.

            **Ref.:** https://bit.ly/3k4whEs


        .. note::

            If an exception is raised, it is caught to be further raised in
            :meth:`input` or :meth:`wait`.

        """
        try:
            # test = 1/0
            self.pin_db.set_pin_state_from_key(self.get_key_name(key), state=HIGH)
        except Exception as e:
            self.th_listener.exc = e

    def update_channel_names(self, new_channel_names):
        """Update the channels names for multiple channels.

        If a channel number is associated with a not yet created :class:`Pin`,
        the corresponding `channel_name` will be temporary saved for later when
        the pin object will be created with :meth:`add_pin`.

        Parameters
        ----------
        new_channel_names : dict
            Dictionary that maps channel numbers (:obj:`int`) to channel names
            (:obj:`str`).

            **Example**::

                new_channel_names = {
                    1: "The Channel 1",
                    2: "The Channel 2"
                }

        """
        # TODO: assert on new_channel_names
        self._update_attribute_pins('channel_name', new_channel_names)

    def update_default_led_symbols(self, new_default_led_symbols):
        """Update the default LED symbols used by all output channels.

        Parameters
        ----------
        new_default_led_symbols : dict
            Dictionary that maps each output state (:obj:`str`, {'`ON`',
            '`OFF`'}) to the LED symbol (:obj:`str`).

            **Example**::

                new_default_led_symbols = {
                    'ON': '🔵',
                    'OFF': '⚪ '
                }

        """
        # TODO: assert on new_led_symbols
        new_default_led_symbols = self._clean_led_symbols(new_default_led_symbols)
        self.default_led_symbols.update(new_default_led_symbols)

    def update_led_symbols(self, new_led_symbols):
        """Update the LED symbols for multiple channels.

        If a channel number is associated with a not yet created :class:`Pin`,
        the corresponding LED symbols will be temporary saved for later when
        the pin object will be created with :meth:`add_pin`.

        Parameters
        ----------
        new_led_symbols : dict
            Dictionary that maps channel numbers (:obj:`int`) to LED symbols
            (:obj:`dict`).

            **Example**::

                new_led_symbols = {
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
        # TODO: assert on new_led_symbols
        self._update_attribute_pins('led_symbols', new_led_symbols)

    # TODO: unique keymap in both ways
    def update_keymap(self, new_keymap):
        """Update the default dictionary mapping keys and GPIO channels.

        ``new_keymap`` is a dictionary mapping some keys to their new GPIO
        channels, and will be used to update the default key-channel mapping
        defined in :mod:`SimulRPi.mapping`.

        Parameters
        ----------
        new_keymap : dict
            Dictionary that maps keys (:obj:`str`) to their new GPIO channels
            (:obj:`int`).

            **Example**::

                new_keymap = {
                    "f": 24,
                    "g": 25,
                    "h": 23
                }

        Raises
        ------
        TypeError
            Raised if a given key is invalid: only special and alphanumeric
            keys recognized by `pynput`_ are accepted.

            See the documentation for :mod:`SimulRPi.mapping` for a list of
            accepted keys.


        .. note::

            If the key to be updated is associated to a channel that is already
            taken by another key, both keys' channels will be swapped. However,
            if any key is being linked to a :obj:`None` channel, then it will take
            on the maximum channel number available + 1.

        """
        # TODO: assert keys (str) and channels (int)
        # TODO: test uniqueness in channel numbers of new map
        assert len(set(new_keymap.values())) == len(new_keymap)
        orig_keych = {}
        for key1, new_ch in new_keymap.items():
            old_ch = self.key_to_channel_map.get(key1)
            # Case 1: if key's channel is not found, maybe it is a special key
            # or an alphanumeric key not already in the keymap
            # Validate the key before updating the keymaps
            if old_ch is None and not self.validate_key(key1):
                # Invalid key: the key is neither a special nor an alphanum key
                orig_keych.setdefault(key1, None)
                raise TypeError("The key '{}' is invalid: only special and "
                                "alphanumeric keys recognized by `pynput` are "
                                "accepted. \nSee the documentation for "
                                "`SimulRPi.mapping` @ https://bit.ly/3fIsd9o "
                                "for a list of accepted keys.".format(key1))
            key2 = self.channel_to_key_map.get(new_ch)
            if key2 is None:
                # Case 2: the new channel is not associated with any key in the
                # keymap. Thus, add the key with the new channel in the keymaps
                orig_keych.setdefault(key1, None)
                self._update_keymaps_and_pin_db(key_channels=[(key1, new_ch)])
                continue
            elif key1 == key2 and new_ch == old_ch:
                # Case 3: No update necessary since the key with the given
                # channel is already in the keymap.
                continue
            else:
                # Case 4: Update the keymaps to reflect the key with the new
                # given channel.
                orig_keych.setdefault(key1, old_ch)
                orig_keych.setdefault(key2, new_ch)
                if old_ch is None:
                    # The new key is not found in the default keymap at all.
                    # Thus, its channel is None and must be set to an integer
                    # channel which is equal to the maximum channel available
                    # plus one. Hence, the second key whose channel is being
                    # swapped with this new key will not receive a None channel
                    # which would be problematic since there can be many keys
                    # with None channels and the keymap channel_to_key_map
                    # would only keep one key with the None channel.
                    old_ch = max(self.channel_to_key_map.keys()) + 1
                self._update_keymaps_and_pin_db(
                    key_channels=[(key1, new_ch), (key2, old_ch)])
        if orig_keych:
            # There were updates and/or there are invalid keys
            msg = "Update of Key-to-Channel Map:\n\n"
            for i, (key, old_ch) in enumerate(orig_keych.items()):
                new_ch = self.key_to_channel_map.get(key)
                msg += '\t Key "{}"{}: Channel {} ------> Channel {}\n'.format(
                    key, " " * (20 - len(key)), old_ch, new_ch)
            logger.debug(msg)

    @staticmethod
    def validate_key(key):
        """Validate if a key is recognized by `pynput`_

        A valid key can either be:

            * a :class:`pynput.keyboard.Key` for special keys (e.g. ``tab`` or \
            ``up``), or
            * a :class:`pynput.keyboard.KeyCode` for normal alphanumeric keys.

        Parameters
        ----------
        key : str
            The key (e.g. '`tab`') that will be validated.

        Returns
        -------
        retval : bool
            Returns `True` if it's a valid key. Otherwise, it returns `False`.

        References
        ----------
        `pynput <https://pynput.readthedocs.io/en/latest/keyboard.html#reference>`__

        See Also
        --------
        :mod:`SimulRPi.mapping` : for a list of special keys supported by
                                  `pynput`_.

        """
        if not hasattr(keyboard.Key, key) and \
                not (len(key) == 1 and key.isalnum()):
            # Unrecognized key
            # Neither a special key nor an alphanum key
            return False
        else:
            return True

    @staticmethod
    def _clean_channel_name(channel_number, channel_name):
        """TODO

        Parameters
        ----------
        channel_number
        channel_name

        Returns
        -------

        """
        return channel_name if channel_name else channel_number

    def _clean_led_symbols(self, led_symbols):
        """TODO

        Parameters
        ----------
        led_symbols

        """
        if led_symbols:
            if led_symbols == "default_ascii":
                led_symbols = {
                    "ON": "\033[1;31;48m(0)\033[1;37;0m",
                    "OFF": "(0)",
                }
            else:
                assert isinstance(led_symbols, dict), \
                    "Wrong type for `led_symbols`: {}. \nIt should be a " \
                    "dictionary".format(led_symbols)
                for symbol_name, symbol_value in led_symbols.items():
                    if symbol_value:
                        symbol_value = symbol_value.replace("\\033", "\033")
                    else:
                        symbol_value = self.default_led_symbols[symbol_name]
                    led_symbols[symbol_name] = symbol_value
        else:
            led_symbols = self.default_led_symbols
        return led_symbols

    def _update_attribute_pins(self, attribute_name, new_attributes):
        """TODO

        Parameters
        ----------
        attribute_name
        new_attributes

        Raises
        ------
        ValueError
            Raised if

        """
        if attribute_name == 'led_symbols':
            set_fnc = self.pin_db.set_pin_symbols_from_channel
        elif attribute_name == 'channel_name':
            set_fnc = self.pin_db.set_pin_name_from_channel
        elif attribute_name == 'channel_id':
            set_fnc = self.pin_db.set_pin_id_from_channel
        else:
            raise ValueError("Invalid attribute name: {}".format(attribute_name))
        for ch_number, attr_value in new_attributes.items():
            # TODO: explain
            ch_number = int(ch_number)
            if attribute_name == 'led_symbols':
                attr_value = self._clean_led_symbols(attr_value)
            elif attribute_name == 'channel_name':
                attr_value = self._clean_channel_name(ch_number, attr_value)
            if not set_fnc(ch_number, attr_value):
                self._channel_tmp_info.setdefault(ch_number, {})
                self._channel_tmp_info[ch_number].update(
                    {attribute_name: attr_value})

    def _update_keymaps_and_pin_db(self, key_channels):
        """Update the two internal keymaps and the pin database.

        :obj:`key_channels` is a list of two-tuples where each tuple contains
        the key and its new channel with which it needs to be updated.

        The different internal data structures need to be updated to reflect
        these changes:

        * the two keymaps :obj:`key_to_channel_map` and \
        :obj:`channel_to_key_map`
        * the pin database who is an instance of :class:`PinDB`

        Parameters
        ----------
        key_channels : list of tuple
            Where each tuple contains the key and its new channel with which it
            needs to be updated.

            **For example**::

                key_channels = [('f', 25), ('g', 23)])

            where the key *'f'* will be mapped to the GPIO channel 25 and the
            key *'g'* to the GPIO channel 23.

        """
        for key_ch in key_channels:
            key = key_ch[0]
            channel = key_ch[1]
            self.key_to_channel_map[key] = channel
            self.channel_to_key_map[channel] = key
            self.pin_db.set_pin_key_from_channel(channel, key)


manager = Manager()


def cleanup():
    """Clean up any resources (e.g. GPIO channels).

    At the end of any program, it is good practice to clean up any resources
    you might have used. This is no different with `RPi.GPIO`_. By returning
    all channels you have used back to inputs with no pull up/down, you can
    avoid accidental damage to your RPi by shorting out the pins.
    [**Ref:** `RPi.GPIO wiki`_]

    Also, the two threads responsible for displaying "LEDs" in the terminal and
    listening for pressed/released keys are stopped.

    .. note::

        On an RPi, :meth:`cleanup` will:

            * only clean up GPIO channels that your script has used
            * also clear the pin numbering system in use (`BOARD` or `BCM`)

        **Ref.:** `RPi.GPIO wiki`_

        When using the package ``SimulRPi``, :meth:`cleanup` will:

            * stop the displaying thread ``Manager.th_display_leds``
            * stop the listener thread ``Manager.th_listener``
            * show the cursor again which was hidden in
              :meth:`Manager.display_leds`
            * reset the ``GPIO.manager``'s attributes (an instance of
              :class:`Manager`)

    """
    # NOTE: global since we are deleting it at the end
    global manager
    # Show cursor again
    # TODO: works on UNIX shell only, not Windows
    # TODO: space at the end?
    os.system("tput cnorm ")
    # Check if displaying thread is alive. If the user didn't setup any output
    # channels for LEDs, then the displaying thread was never started
    if manager.th_display_leds.is_alive():
        manager.th_display_leds.do_run = False
        manager.th_display_leds.join()
        logger.debug("Thread stopped: {}".format(manager.th_display_leds.name))
    # Check if listener thread is alive. If the user didn't setup any input
    # channels for buttons, then the listener thread was never started
    if manager.th_listener and manager.th_listener.is_alive():
        logger.debug("Stopping thread: {}".format(manager.th_listener.name))
        manager.th_listener.stop()
        logger.debug("Thread stopped: {}".format(manager.th_listener.name))
    # Reset Manager's attributes
    del manager
    manager = Manager()


def input(channel):
    """Read the value of a GPIO pin.

    Parameters
    ----------
    channel : int
        Input channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).

    Returns
    -------
    state : :obj:`int` or :obj:`None`
        If no :class:`Pin` could be retrieved based on the given channel
        number, then :obj:`None` is returned. Otherwise, the :class:`Pin`\'s
        state is returned: 1 (`HIGH`) or 0 (`LOW`).

    Raises
    ------
    Exception
        If the listening thread caught an exception that occurred in
        :meth:`Manager.on_press` and
        :meth:`Manager.on_release`, the said exception will be raised
        here.


    .. note::

        The listener thread (for monitoring pressed key) is started if it is
        not alive, i.e. it is not already running.

    """
    # Start the listener thread only if it is not already alive and there is no
    # exception in the thread's target function
    if manager.th_listener:
        if not manager.th_listener.exc and not manager.th_listener.is_alive():
            manager.th_listener.start()
        _raise_if_thread_exception(manager.th_listener.name)
    return manager.pin_db.get_pin_state(channel)


# TODO: output to several channels, see https://bit.ly/2Dgk2Uf
def output(channel, state):
    """Set the output state of a GPIO pin.

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

            GPIO.output(chan_list, GPIO.LOW)               # sets all to LOW
            GPIO.output(chan_list, (GPIO.HIGH, GPIO.LOW))  # sets 1st HIGH and 2nd LOW.

    Raises
    ------
    Exception
        If the displaying thread caught an exception that occurred in its
        target function, the said exception will be raised here.


    .. note::

        The displaying thread (for showing "LEDs" on the terminal) is started
        if there is no exception caught by the thread and if it is not alive,
        i.e. it is not already running.

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
    If no channel name given, then the channel number will be shown.

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
        * ``key``: keyboard key associated with a channel, e.g. "cmd_r".

    Parameters
    ----------
    gpio_channels : list
        A list where each item is a dictionary defining the attributes for a
        given GPIO channel. This list corresponds to the main configuration's
        setting `gpio_channels` (See `here`_).

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
    default_led_symbols : dict
        Dictionary that maps each output state (:obj:`str`, {'`ON`',
        '`OFF`'}) to the LED symbol (:obj:`str`).

        **Example**::

            default_led_symbols = {
                'ON': '🔵',
                'OFF': '⚪ '
            }

    """
    manager.update_default_led_symbols(default_led_symbols)


# TODO: explain that the mapping is unique in both ways, i.e. one keyboard key
# can only be associated to a one GPIO channel, and vice versa.
def setkeymap(key_to_channel_map):
    """Set the keymap dictionary with new keys and channels.

    The default dictionary `default_key_to_channel_map`_ (defined in
    :mod:`SimulRPi.mapping`) that maps keyboard keys to GPIO channels can be
    modified by providing your own mapping ``key_to_channel_map`` containing
    only the keys and channels that you want to be modified.

    Parameters
    ----------
    key_to_channel_map : dict
        A dictionary mapping keys (:obj:`str`) to GPIO channel numbers
        (:obj:`int`) that will be used to update the default keymap found in
        :mod:`SimulRPi.mapping`.

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
    `RPi.GPIO`.

    There are two ways of numbering the I/O pins on a Raspberry Pi within
    `RPi.GPIO`:

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


# TODO: setup more than one channel, see https://bit.ly/2Dgk2Uf
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
    your Raspberry Pi. As a result of this, if RPi.GPIO detects that a pin has
    been configured to something other than the default (input), you get a
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
    was an exception caught by one thread, then it is raised here.

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
        :meth:`cleanup` is found in a ``finally`` block:

        .. code-block:: python
           :emphasize-lines: 7

           try:
               do_something_with_gpio_api()
               GPIO.wait()
           except Exception as e:
               # Do something with error
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
    which_threads

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
