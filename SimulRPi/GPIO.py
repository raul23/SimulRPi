"""Module that partly fakes `RPi.GPIO`_ and simulates some I/O devices.

It simulates these I/O devices connected to a Raspberry Pi:

    - push buttons by listening to pressed keyboard keys and
    - LEDs by displaying small circles blinking on the terminal along with \
    their GPIO pin number.

When a LED is turned on, it is shown as a small red circle on the terminal. The
package `pynput`_ is used to monitor the keyboard for any pressed key.

..
    TODO: also found in README_docs

.. highlight:: none

**Example: terminal output** ::

    o [11]   o [9]   o [10]

.. highlight:: python

where each circle represents a LED (here they are all turned off) and the number
between brackets is the associated GPIO pin number.

.. important::

    This library is not a Raspberry Pi emulator nor a complete mock-up of
    `RPi.GPIO`_, only the most important functions that I needed for my
    `Darth-Vader-RPi project`_ were added.

    If there is enough interest in this library, I will eventually mock more
    functions from `RPi.GPIO`_. Thus,
    `let me know through SimulRPi's issues page`_ if you want me to add more
    things to this library.

..
    TODO: also found in README_docs.rst

.. _Darth-Vader-RPi project: https://github.com/raul23/Darth-Vader-RPi
.. _let me know through SimulRPi's issues page:
    https://github.com/raul23/SimulRPi/issues
.. _pynput: https://pynput.readthedocs.io/en/latest/index.html
.. _RPi.GPIO: https://pypi.org/project/RPi.GPIO/
.. _RPi.GPIO wiki: https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/

"""
import copy
import logging
import os
import threading
from logging import NullHandler

try:
    from pynput import keyboard
except ImportError:
    print("`pynput` couldn't be found. Thus, no keyboard keys will be detected "
          "if pressed or released.\nIf you need this option, install pynput "
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


class ExceptionThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.exc = None

    def run(self):
        try:
            self._target(*self._args, **self._kwargs)
        except Exception as e:
            self.exc = e


class Pin:
    """Class that represents a GPIO pin.

    Parameters
    ----------
    channel_number : int
        GPIO channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).
    channel_id : str
        TODO
    gpio_function : int
        Function of a GPIO channel: 1 (`GPIO.INPUT`) or 0 (`GPIO.OUTPUT`).
    channel_name : str, optional
        TODO
    key : str or None, optional
        Keyboard key associated with the GPIO channel, e.g. "k".
    led_symbols : dict, optional
        TODO
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
    def __init__(self, channel_number, channel_id, gpio_function,
                 channel_name=None, key=None, led_symbols=None,
                 pull_up_down=None, initial=None):
        self.channel_number = channel_number
        self.channel_id = channel_id
        self.gpio_function = gpio_function
        self.channel_name = channel_name
        self.key = key
        self.pull_up_down = pull_up_down
        self.initial = initial
        self.led_symbols = led_symbols
        if gpio_function == IN:
            self.state = HIGH
        else:
            self.state = LOW


class PinDB:
    """Class for storing and modifying :class:`Pin`\s.

    Each instance of :class:`GPIO.Pin` is saved in a dictionary that maps it
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
        self.output_pins = []

    def create_pin(self, channel_number, channel_id, gpio_function, **kwargs):
        """Create an instance of :class:`GPIO.Pin` and save it in a dictionary.

        Based on the given arguments, an instance of :class:`GPIO.Pin` is
        created and added to a dictionary that acts like a database of pins
        with key being the pin's channel and the value is an instance of
        :class:`Pin`.

        Parameters
        ----------
        channel_number : int
            GPIO channel number based on the numbering system you have specified
            (`BOARD` or `BCM`).
        channel_id : str
            TODO
        gpio_function : int
            Function of a GPIO channel: 1 (`GPIO.INPUT`) or 0 (`GPIO.OUTPUT`).
        kwargs :
            TODO

        """
        self._pins[channel_number] = Pin(channel_number, channel_id,
                                         gpio_function, **kwargs)
        if gpio_function == OUT:
            # OUTPUT pin (e.g. LED)
            # Save the output pin so the thread that displays LEDs knows what
            # pins are OUTPUT and therefore connected to LEDs.
            self.output_pins.append(self._pins[channel_number])
        # Update the other internal dict if key is given
        if kwargs['key']:
            # Input
            # TODO: assert on gpop_function which should be INPUT?
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
        Pin : :class:`GPIO.Pin` or :obj:`None`
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
        Pin : :class:`GPIO.Pin` or :obj:`None`
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
        state : int or :obj:`None`
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
        :attr:`key` is set with `key`.

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

    def set_pin_name_from_channel(self, channel_number, name):
        """TODO

        Parameters
        ----------
        channel_number
        name

        Returns
        -------

        """
        pin = self.get_pin_from_channel(channel_number)
        if pin:
            # TODO: only update name if the name is different from the actual
            pin.name = name
            return True
        else:
            return False

    def set_pin_symbols_from_channel(self, channel_number, led_symbols):
        """TODO

        Parameters
        ----------
        channel_number
        led_symbols

        Returns
        -------

        """
        pin = self.get_pin_from_channel(channel_number)
        if pin:
            # TODO: only update symbols if the symbols is different from the actual
            pin.led_symbols = led_symbols
            return True
        else:
            return False

    def set_pin_id_from_channel(self, channel_number, channel_id):
        """TODO

        Parameters
        ----------
        channel_number
        channel_id

        Returns
        -------

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
        :attr:`state` is set with `state`.

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
            `state`. Otherwise, it returns `False` because the pin doesn't
            exist based on the given `channel`.

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
        :attr:`state` is set with `state`.

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
            `state`. Otherwise, it returns `False` because the pin doesn't
            exist based on the given `key`.

        """
        pin = self.get_pin_from_key(key)
        if pin:
            # TODO: only update state if the state is different from the actual
            pin.state = state
            return True
        else:
            return False


class Manager:
    """Class that manages the pin database (:class:`PinDB`) and the threads
    responsible for displaying "LEDs" on the terminal and listening for keys
    pressed/released.

    The threads are not started right away in :meth:`__init__` but in
    :meth:`input` for the listener thread and :meth:`output` for the
    displaying thread.

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
        A :class:`Pin` database. See :class:`PinDB` on how to access it.
    default_led_symbols : dict
        A dictionary that maps ... TODO
    key_to_channel_map : dict
        A dictionary that maps keyboard keys (:obj:`string`) to GPIO channel
        numbers (:obj:`int`). By default, it takes the keys and values defined
        in :mod:`SimulRPi.mapping`'s keymap ``default_key_to_channel_map``.
    channel_to_key_map : dict
        The reverse dictionary of :attr:`key_to_channel_map`. It maps channels
        to keys.
    th_display_leds : threading.Thread
        Thread responsible for displaying small blinking circles on the
        terminal as to simulate LEDs connected to an RPi.
    th_listener : keyboard.Listener
        Thread responsible for listening on any pressed or released key as to
        simulate push buttons connected to an RPi.

        .. note::

            A keyboard listener is a :class:`threading.Thread`, and all
            callbacks will be invoked from the thread.

            **Ref.:** https://pynput.readthedocs.io/en/latest/keyboard.html#monitoring-the-keyboard


    .. important::

        If the module :mod:`pynput.keyboard` couldn't be imported, the
        listener thread :attr:`th_listener` will not be created and the parts
        of the ``SimulRPi`` library that monitors the keyboard for any pressed
        or released key will be ignored. Only the thread
        :attr:`th_display_leds` that displays "LEDs" on the terminal will be
        created.

        This is necessary for example in the case we are running tests on
        travis and we don't want travis to install ``pynput`` in a headless
        setup because an exception will get raised::

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
            "OFF": "\U000026AA",
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
            self.th_listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release)
            self.th_listener.name = "thread_listener"
        else:
            self.th_listener = None

    def add_pin(self, channel_number, gpio_function, pull_up_down=None, initial=None):
        """Add an input or output pin to the pin database.

        An instance of :class:`Pin` is created with the given arguments and
        added to the pin database :class:`PinDB`.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` to be added in
            the pin database.
        gpio_function : int
            Function of a GPIO channel: 1 (`GPIO.INPUT`) or 0 (`GPIO.OUTPUT`).
        pull_up_down : int or None, optional
            Initial value of an input channel, e.g. `GPIO.PUP_UP`. Default
            value is :obj:`None`.
        initial : int or None, optional
            Initial value of an output channel, e.g. `GPIO.HIGH`. Default value
            is :obj:`None`.

        """
        key = None
        if gpio_function == IN:
            # Get keyboard key associated with the INPUT pin (button)
            # TODO: raise exception if key not found
            # TODO: add key also in _channel_tmp_info?
            key = self.channel_to_key_map.get(channel_number)
        tmp_info = self._get_tmp_info(channel_number)
        if self._channel_tmp_info.get(channel_number):
            del self._channel_tmp_info[channel_number]
        self.pin_db.create_pin(
            channel_number=channel_number,
            channel_id=tmp_info.get('channel_id', channel_number),
            gpio_function=gpio_function,
            channel_name=tmp_info.get('channel_name', channel_number),
            key=key,
            led_symbols=tmp_info.get('led_symbols', self.default_led_symbols),
            pull_up_down=pull_up_down,
            initial=initial)

    def _get_tmp_info(self, channel_number):
        """TODO

        Parameters
        ----------
        channel_number

        Returns
        -------

        """
        retval = {}
        attribute_names = ['channel_id', 'channel_name', 'led_symbols']
        ch_info = self._channel_tmp_info.get(channel_number)
        if ch_info:
            for attr_name in attribute_names:
                attr_value = ch_info.get(attr_name)
                if attr_name == 'led_symbols':
                    if attr_value:
                        # TODO: explain
                        for k, v in attr_value.items():
                            v = v.replace("\\033", "\033")
                            attr_value[k] = v
                    attr_value = attr_value if attr_value else self.default_led_symbols
                else:
                    # channel_id and channel_name
                    attr_value = attr_value if attr_value else channel_number
                retval.setdefault(attr_name, attr_value)
        return retval

    def display_leds(self):
        """Simulate LEDs on an RPi by blinking small circles on a terminal.

        In order to simulate LEDs turning on/off on an RPi, small circles are
        blinked on the terminal along with their GPIO pin number.

        When a LED is turned on, it is shown as a small red circle on the
        terminal.

        .. highlight:: none

        **Example: terminal output** ::

            o [11]   o [9]   o [10]

        .. highlight:: python

        where each circle represents a LED (here they are all turned off) and
        the number between brackets is the associated GPIO pin number.

        .. note::

            If :attr:`enable_printing` is set to `True`, the terminal's cursor
            will be hidden. It will be eventually shown again in :meth:`cleanup`
            which is called by the main program when it is exiting.

            The reason is to avoid messing with the display of LEDs by the
            displaying thread :attr:`th_display_leds`.

        .. important::

            :meth:`display_leds` should be run by a thread and eventually
            stopped from the main thread by setting its ``do_run`` attribute to
            `False` to let the thread exit from its target function.

            **For example**:

            .. code-block:: python

                th = threading.Thread(target=self.display_leds, args=())
                th.start()

                # Your other code ...

                # Time to stop thread
                th.do_run = False
                th.join()

        """
        # TODO: explain order outputs are setup is how the channels are shown
        if self.enable_printing:
            # Hide the cursor
            os.system("tput civis")
            print()
        th = threading.currentThread()
        # TODO: reduce number of prints, i.e. computations
        while getattr(th, "do_run", True):
            leds = ""
            last_msg_length = len(leds) if leds else 0
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
        logger.debug("Stopping thread: {}".format(th.name))

    @staticmethod
    def get_key_name(key):
        """Get the name of a keyboard key as a string.

        The name of the special or alphanumeric key is given by the package
        `pynput`_.

        Parameters
        ----------
        key : pynput.keyboard.Key or pynput.keyboard.KeyCode
            The keyboard key (from :mod:`pynput.keyboard`) whose name will be
            returned.

        Returns
        -------
        key_name : str or None
            Returns the name of the given keyboard key if one was found by
            `pynput`_. Otherwise, it returns :obj:`None`.

        """
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

        Callback invoked from the thread :attr:`GPIO.Manager.th_listener`.

        This thread is used to monitor the keyboard for any valid pressed key.
        Only keys defined in the pin database are treated, i.e. keys that were
        configured with :meth:`GPIO.setup` are further processed.

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

        """
        self.pin_db.set_pin_state_from_key(self.get_key_name(key), state=LOW)

    def on_release(self, key):
        """When a valid keyboard key is released, set its state to `GPIO.HIGH`.

        Callback invoked from the thread :attr:`GPIO.Manager.th_listener`.

        This thread is used to monitor the keyboard for any valid released key.
        Only keys defined in the pin database are treated, i.e. keys that were
        configured with :meth:`GPIO.setup` are further processed.

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

        """
        self.pin_db.set_pin_state_from_key(self.get_key_name(key), state=HIGH)

    def bulk_update_channel_tmp_info(self, new_channel_tmp_info):
        for ch_number, ch_attributes in new_channel_tmp_info.items():
            for attribute_name, attribute_value in ch_attributes.items():
                self._update_attribute_pins(
                    attribute_name,
                    {ch_number: {attribute_name: attribute_value}})

    def update_channel_ids(self, new_channel_ids):
        """TODO

        Parameters
        ----------
        new_channel_ids : dict
            Dictionary that maps channel number to channel id.

        Returns
        -------

        """
        # TODO: assert on new_channel_names
        self._update_attribute_pins('channel_id', new_channel_ids)

    def update_channel_names(self, new_channel_names):
        """TODO

        Parameters
        ----------
        new_channel_names : dict
            Dictionary that maps channel number to channel name.

        Returns
        -------

        """
        # TODO: assert on new_channel_names
        self._update_attribute_pins('channel_name', new_channel_names)

    def update_default_led_symbols(self, new_default_led_symbols):
        """TODO

        Parameters
        ----------
        new_default_led_symbols

        Returns
        -------

        """
        # TODO: assert on new_led_symbols
        self.default_led_symbols.update(new_default_led_symbols)

    def update_led_symbols(self, new_led_symbols):
        """TODO

        Parameters
        ----------
        new_led_symbols

        Returns
        -------

        """
        # TODO: assert on new_led_symbols
        self._update_attribute_pins('led_symbols', new_led_symbols)

    def _update_attribute_pins(self, attribute_name, new_attributes):
        if attribute_name == 'led_symbols':
            set_fnc = self.pin_db.set_pin_symbols_from_channel
        elif attribute_name == 'channel_name':
            set_fnc = self.pin_db.set_pin_name_from_channel
        elif attribute_name == 'channel_id':
            set_fnc = self.pin_db.set_pin_id_from_channel
        else:
            raise ValueError("Invalid attribute name: {}".format(attribute_name))
        for ch_number, attribute_dict in new_attributes.items():
            # TODO: explain
            if not set_fnc(ch_number, attribute_dict):
                self._channel_tmp_info.setdefault(ch_number, {})
                self._channel_tmp_info[ch_number].update(attribute_dict)

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

            **For example**::

                "key_to_channel_map":
                {
                    "f": 24,
                    "g": 25,
                    "h": 23
                }


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
            msg = "Update of Key-to-Channel Map:\n"
            for key, old_ch in orig_keych.items():
                new_ch = self.key_to_channel_map.get(key)
                msg += 'Key "{}": Channel {} ------> Channel {}\n'.format(
                    key, old_ch, new_ch)
            logger.info(msg)

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
        :mod:`pynput` reference: https://pynput.readthedocs.io/en/latest/keyboard.html#reference

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

    Also, the two threads responsible for displaying "LEDs" on the terminal and
    listening for pressed/released keys are stopped.

    .. note::

        On an RPi, :meth:`cleanup` will:

            * only clean up GPIO channels that your script has used
            * also clear the pin numbering system in use (`BOARD` or `BCM`)

        **Ref.:** `RPi.GPIO wiki`_

        When using the package ``SimulRPi``, :meth:`cleanup` will:

            * stop the displaying thread :attr:`Manager.th_display_leds`
            * stop the listener thread :attr:`Manager.th_listener`
            * show the cursor again which was hidden in \
            :meth:`Manager.display_leds`
            * reset the :obj:`GPIO.manager`'s attributes (an instance of \
            :class:`Manager`)

    """
    global manager
    # Show cursor again
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


def input(channel_number):
    """Read the value of a GPIO pin.

    Parameters
    ----------
    channel_number : int
        Input GPIO channel number based on the numbering system you have
        specified (`BOARD` or `BCM`).

    Returns
    -------
    state : int or :obj:`None`
        If no :class:`Pin` could be retrieved based on the given channel
        number, then :obj:`None` is returned. Otherwise, the :class:`Pin`\'s
        state is returned: 1 (`HIGH`) or 0 (`LOW`).


    .. note::

        The listener thread (for monitoring pressed key) is started if it is
        not alive, i.e. it is not already running.

    """
    # Start the listener thread only if it not already alive
    if manager.th_listener and not manager.th_listener.is_alive():
        manager.th_listener.start()
    return manager.pin_db.get_pin_state(channel_number)


# TODO: output to several channels, see https://bit.ly/2Dgk2Uf
def output(channel_number, state):
    """Set the output state of a GPIO pin.

    Parameters
    ----------
    channel_number : int
        Output GPIO channel number based on the numbering system you have
        specified (`BOARD` or `BCM`).
    state : int
        State of the GPIO channel: 1 (`HIGH`) or 0 (`LOW`).


    .. note::

        The displaying thread (for showing "LEDs" on the terminal) is started
        if it is not alive, i.e. it is not already running.

    """
    manager.pin_db.set_pin_state_from_channel(channel_number, state)
    # Start the displaying thread only if it not already alive
    if not manager.th_display_leds.exc and \
            not manager.th_display_leds.is_alive():
        manager.th_display_leds.start()
    if manager.th_display_leds.exc and manager.th_display_leds.exc != "exception_found":
        # Happens when error in Manager.display_leds()
        exc = manager.th_display_leds.exc
        manager.th_display_leds.exc = "exception_found"
        raise exc


def setchannelnames(channel_names):
    """TODO

    Parameters
    ----------
    channel_names

    """
    manager.update_channel_names(channel_names)


def setchannels(gpio_channels):
    """TODO

    Parameters
    ----------
    gpio_channels

    """
    pins_tmp_info = {}
    key_maps = {}
    for gpio_ch in gpio_channels:
        channel_id = gpio_ch.get('channel_id')
        channel_name = gpio_ch.get('channel_name')
        channel_number = gpio_ch.get('channel_number')
        led_symbols = gpio_ch.get('led_symbols')
        pins_tmp_info.setdefault(channel_number, {})
        pins_tmp_info[channel_number] = {
            'channel_id': channel_id,
            'channel_name': channel_name,
            'led_symbols': led_symbols
        }
        if gpio_ch.get('key'):
            key_maps.update({gpio_ch.get('key'): channel_number})
    manager.bulk_update_channel_tmp_info(pins_tmp_info)
    setkeymap(key_maps)


# TODO: explain that the mapping is unique in both ways, i.e. one keyboard key
# can only be associated to a one GPIO channel, and vice versa.
def setkeymap(key_to_channel_map):
    """Set the keymap dictionary with new keys and channels.

    The default dictionary :obj:`default_key_to_channel_map` (defined in
    :mod:`SimulRPi.mapping`) that maps keyboard keys to GPIO channels can be
    modified by providing your own mapping ``key_to_channel_map`` containing
    only the keys and channels that you want to be modified.

    Parameters
    ----------
    key_to_channel_map : dict
        A dictionary mapping keys (:obj:`str`) and GPIO channels (:obj:`int`)
        that will be used to update the default keymap found in
        :mod:`SimulRPi.mapping`.

        **For example**::

            key_to_channel_map:
            {
                "q": 23,
                "w": 24,
                "e": 25
            }

    """
    manager.update_keymap(key_to_channel_map)


def setdefaultsymbols(default_led_symbols):
    """TODO

    Parameters
    ----------
    default_led_symbols

    """
    manager.update_default_led_symbols(default_led_symbols)


def setsymbols(led_symbols):
    """TODO

    Parameters
    ----------
    led_symbols

    """
    manager.update_led_symbols(led_symbols)


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
    """Enable printing on the terminal.

    If printing is enabled, small blinking red circles will be shown on the
    terminal, simulating LEDs connected to a Raspberry Pi. Otherwise, nothing
    will be printed on the terminal.

    Parameters
    ----------
    enable_printing : bool
        Whether to enable printing on the terminal.

    """
    # TODO: stop displaying thread too?
    manager.enable_printing = enable_printing


# TODO: setup more than one channel, see https://bit.ly/2Dgk2Uf
def setup(channel, gpio_function, pull_up_down=None, initial=None):
    """Setup a GPIO channel as an input or output.

    To configure a channel as an input::

        GPIO.setup(channel, GPIO.IN)

    To configure a channel as an output::

        GPIO.setup(channel, GPIO.OUT)

    You can also specify an initial value for your output channel::

        GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)

    Parameters
    ----------
    channel : int
        GPIO channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).
    gpio_function : int
        Function of a GPIO channel: 1 (`GPIO.INPUT`) or 0 (`GPIO.OUTPUT`).
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
    # TODO: assert on mode
    manager.add_pin(channel, gpio_function, pull_up_down, initial)


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
