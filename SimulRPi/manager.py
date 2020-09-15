"""Module that manages the :class:`~SimulRPi.pindb.PinDB` database, threads,
and default keymap.

The threads are responsible for displaying LEDs in the terminal and listening
to the keyboard.

The default keymap maps keyboard keys to GPIO channel numbers and is defined
in `default_key_to_channel_map`_.

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
          "if pressed or released.\nIf you need this option, install `pynput` "
          "with: pip install pynput.\n")
    keyboard = None

# NOTE: on Python 3.5 and 3.6, can't use ``import SimulRPi.GPIO as GPIO``
# if circular import
# AttributeError: module 'SimulRPi' has no attribute 'GPIO
import SimulRPi.GPIO
from SimulRPi.mapping import default_key_to_channel_map
from SimulRPi.pindb import PinDB

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())


class DisplayExceptionThread(threading.Thread):
    """A subclass from :class:`threading.Thread` that defines threads that can
    catch errors if their target functions raise an exception.

    Attributes
    ----------
    exception_raised : bool
        When the exception is raised, it should be set to `True`. By default, it
        is `False`.
    exc: :class:`Exception`
        Represents the exception raised by the target function.

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

        **It also catches and saves any error that the target function might
        raise.**

        .. important::

            The exception is only caught here, not raised. The exception is
            further raised in :meth:`SimulRPi.GPIO.output` or
            :meth:`SimulRPi.GPIO.wait`. The reason for not raising it here is
            because the main program won't catch it. The exception must be
            raised outside the thread's ``run`` method so that the thread's
            exception can be caught by the main program.

            The same reasoning applies to the listening thread's callbacks
            :meth:`Manager.on_press` and :meth:`Manager.on_release`.

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

        # TODO: check if you can modify run() like you did for DisplayExceptionThread
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.exception_raised = False
            self.exc = None


class Manager:
    """Class that manages the pin database (:class:`SimulRPi.pindb.PinDB`),
    the threads responsible for displaying "LEDs" in the terminal and listening
    for pressed/released keys, and the default keymap.

    The threads are not started right away in ``__init__()`` but in
    :meth:`SimulRPi.GPIO.input` for the listening thread and
    :meth:`SimulRPi.GPIO.output` for the displaying thread.

    They are eventually stopped in :meth:`SimulRPi.GPIO.cleanup`.

    The default keymap maps keyboard keys to GPIO channel numbers and is defined
    in `default_key_to_channel_map`_.

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
        A database of :class:`~SimulRPi.pindb.Pin`\s. See
        :class:`~SimulRPi.pindb.PinDB` on how to access it.
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
    th_display_leds : manager.DisplayExceptionThread
        Thread responsible for displaying blinking red dots in the terminal as
        to simulate LEDs connected to an RPi.
    th_listener : manager.KeyboardExceptionThread
        Thread responsible for listening on any pressed or released keyboard
        key as to simulate push buttons connected to an RPi.

        If ``pynput`` couldn't be imported, ``th_listener`` is :obj:`None`.
        Otherwise, it is instantiated from ``manager.KeyboardExceptionThread``.

        .. note::

            A keyboard listener is a subclass of :class:`threading.Thread`, and
            all callbacks will be invoked from the thread.

            **Ref.:** https://pynput.readthedocs.io/en/latest/keyboard.html#monitoring-the-keyboard


    .. important::

        If the ``pynput.keyboard`` module couldn't be imported, the listening
        thread ``th_listener`` will not be created and the parts of the
        ``SimulRPi`` library that monitors the keyboard for any pressed or
        released key will be ignored. Only the thread ``th_display_leds`` that
        displays "LEDs" in the terminal will be created.

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
        self.th_display_leds = DisplayExceptionThread(
            name="thread_display_leds",
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

        An instance of :class:`~SimulRPi.pindb.Pin` is created with the given
        arguments and added to the pin database :class:`~SimulRPi.pindb.PinDB`.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the
            :class:`~SimulRPi.pindb.Pin` to be added in the pin database.
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
        if channel_type == SimulRPi.GPIO.IN:
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

        If a channel number is associated with a not yet created
        :class:`~SimulRPi.pindb.Pin`, the corresponding attributes will be
        temporary saved for later when the pin object will be created with
        :meth:`add_pin`.

        Parameters
        ----------
        new_channels_attributes : dict
            A dictionary mapping channel numbers (:obj:`int`) with channels'
            attributes (:obj:`dict`). The accepted attributes are those
            specified in :meth:`SimulRPi.GPIO.setchannels`.

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
        """Displaying thread's **target function** that simulates LEDs
        connected to an RPi by blinking red dots in a terminal.

        .. highlight:: none

        **Example: terminal output** ::

            ⬤ [9]   ⬤ [10]   🔴 [11]

        .. highlight:: python

        where each dot represents a LED and the number between brackets is the
        associated GPIO channel number.

        .. important::

            :meth:`display_leds` should be run by a thread and eventually
            stopped from the main program by setting its ``do_run`` attribute
            to `False` to let the thread exit from its target function.

            **For example**:

            .. code-block:: python

                th = DisplayExceptionThread(target=self.display_leds, args=())
                th.start()

                # Your other code ...

                # Time to stop thread
                th.do_run = False
                th.join()

        .. note::

            If ``enable_printing`` is set to `True`, the terminal's cursor will
            be hidden. It will be eventually shown again in
            :meth:`SimulRPi.GPIO.cleanup` which is called by the main program
            when it is exiting.

            The reason is to avoid messing with the display of LEDs done by the
            displaying thread ``th_display_leds``.

        .. note::

            Since the displaying thread ``th_display_leds`` is an
            :class:`DisplayExceptionThread` object, it has an attribute ``exc``
            which stores the exception raised by this target function.

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
                if pin.state == SimulRPi.GPIO.HIGH:
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

        The name of the special or alphanumeric key is given by the `pynput`_
        package.

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
        """When a valid keyboard key is pressed, set the associated pin's
        state to `GPIO.LOW`.

        **Callback** invoked from the thread ``th_listener``.

        This thread is used to monitor the keyboard for any valid pressed key.
        Only keys defined in the pin database are treated, i.e. keys that were
        configured with :meth:`SimulRPi.GPIO.setup` are further processed.

        Once a valid key is detected as pressed, the associated pin's state is
        changed to `GPIO.LOW`.

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
            :meth:`SimulRPi.GPIO.input` or :meth:`SimulRPi.GPIO.wait`.

        See Also
        --------
        :meth:`DisplayExceptionThread`:  Read the **Important** message that
                                         explains why an exception is not
                                         raised in a thread's callback or
                                         target function.

        """
        try:
            # test = 1/0
            self.pin_db.set_pin_state_from_key(self.get_key_name(key),
                                               state=SimulRPi.GPIO.LOW)
        except Exception as e:
            self.th_listener.exc = e

    def on_release(self, key):
        """When a valid keyboard key is released, set the associated pin's
        state to `GPIO.HIGH`.

        **Callback** invoked from the thread ``th_listener``.

        This thread is used to monitor the keyboard for any valid released key.
        Only keys defined in the pin database are treated, i.e. keys that were
        configured with :meth:`SimulRPi.GPIO.setup` are further processed.

        Once a valid key is detected as released, the associated pin's state is
        changed to `GPIO.HIGH`.

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
            :meth:`SimulRPi.GPIO.input` or :meth:`SimulRPi.GPIO.wait`.

        See Also
        --------
        :meth:`DisplayExceptionThread`:  Read the **Important** message that
                                         explains why an exception is not
                                         raised in a thread's callback or
                                         target function.

        """
        try:
            # test = 1/0
            self.pin_db.set_pin_state_from_key(self.get_key_name(key),
                                               state=SimulRPi.GPIO.HIGH)
        except Exception as e:
            self.th_listener.exc = e

    def update_channel_names(self, new_channel_names):
        """Update the channels names for multiple channels.

        If a channel number is associated with a not yet created
        :class:`~SimulRPi.pindb.Pin`, the corresponding `channel_name` will be
        temporary saved for later when the pin object will be created with
        :meth:`add_pin`.

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
            '`OFF`'}) to a LED symbol (:obj:`str`).

            **Example**::

                new_default_led_symbols = {
                    'ON': '🔵',
                    'OFF': '⚪ '
                }

        """
        # TODO: assert on new_led_symbols
        new_default_led_symbols = self._clean_led_symbols(new_default_led_symbols)
        self.default_led_symbols.update(new_default_led_symbols)

    # TODO: unique keymap in both ways
    def update_keymap(self, new_keymap):
        """Update the default dictionary mapping keys and GPIO channels.

        ``new_keymap`` is a dictionary mapping some keys to their new GPIO
        channels, and will be used to update the default keymap
        `default_key_to_channel_map`_.

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
            if a key is being linked to a :obj:`None` channel, then it will
            take on the maximum channel number available + 1.

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

    def update_led_symbols(self, new_led_symbols):
        """Update the LED symbols for multiple channels.

        If a channel number is associated with a not yet created
        :class:`~SimulRPi.pindb.Pin`, the corresponding LED symbols will be
        temporary saved for later when the pin object will be created with
        :meth:`add_pin`.

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

        ``key_channels`` is a list of two-tuples where each tuple contains the
        key and its new channel with which it needs to be updated.

        The different internal data structures need to be updated to reflect
        these changes:

        * the two keymaps ``key_to_channel_map`` and ``channel_to_key_map``
        * the pin database (:class:`SimulRPi.pindb.PinDB`)

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
