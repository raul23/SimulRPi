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
    things to this mock library.

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

from pynput import keyboard

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


class Pin:
    """Class that represents a GPIO pin.

    Parameters
    ----------
    channel : int
        GPIO channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).
    gpio_function : int
        Function of a GPIO channel: 1 (`GPIO.INPUT`) or 0 (`GPIO.OUTPUT`).
    key : str or None, optional
        Key associated with the GPIO channel, e.g. "k".
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
    def __init__(self, channel, gpio_function, key=None, pull_up_down=None,
                 initial=None):
        self.channel = channel
        self.gpio_function = gpio_function
        self.key = key
        self.pull_up_down = pull_up_down
        self.initial = initial
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
        self._pins = {}
        # The other dict is only for INPUT channels with an associated key
        # TODO: explain more
        self._key_to_pin_map = {}

    def create_pin(self, channel, gpio_function, key=None, pull_up_down=None,
                   initial=None):
        """Create an instance of :class:`GPIO.Pin` and save it in a dictionary.

        Based on the given arguments, an instance of :class:`GPIO.Pin` is
        created and added to a dictionary that acts like a database of pins
        with key being the pin's channel and the value is an instance of
        :class:`Pin`.

        Parameters
        ----------
        channel : int
            GPIO channel number based on the numbering system you have
            specified (`BOARD` or `BCM`).
        gpio_function : int
            Function of a GPIO channel: 1 (`GPIO.INPUT`) or 0 (`GPIO.OUTPUT`).
        key : str or None, optional
            Key associated with the GPIO channel, e.g. "k".
        pull_up_down : int or None, optional
            Initial value of an input channel, e.g. `GPIO.PUP_UP`. Default
            value is :obj:`None`.
        initial : int or None, optional
            Initial value of an output channel, e.g. `GPIO.HIGH`. Default value
            is :obj:`None`.

        """
        self._pins[channel] = Pin(channel, gpio_function, key, pull_up_down,
                                  initial)
        # Update the other internal dict if key is given
        if key:
            # Input
            # TODO: assert on gpop_function which should be INPUT?
            self._key_to_pin_map[key] = self._pins[channel]

    def get_pin_from_channel(self, channel):
        """Get a :class:`Pin` from a given channel.

        Parameters
        ----------
        channel : int
            GPIO channel number associated with the :class:`Pin` to be
            retrieved.

        Returns
        -------
        Pin : :class:`GPIO.Pin` or :obj:`None`
            If no :class:`Pin` could be retrieved based on the given channel,
            :obj:`None` is returned. Otherwise, a :class:`Pin` object is
            returned.

        """
        return self._pins.get(channel)

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

    def get_pin_state(self, channel):
        """Get a :class:`Pin`\'s state from a given channel.

        The state associated with a :class:`Pin` can either be 1 (`HIGH`) or 0
        (`LOW`).

        Parameters
        ----------
        channel : int
            GPIO channel number associated with the :class:`Pin` whose state is
            to be returned.

        Returns
        -------
        state : int or :obj:`None`
            If no :class:`Pin` could be retrieved based on the given channel
            number, then :obj:`None` is returned. Otherwise, the
            :class:`Pin`\'s state is returned: 1 (`HIGH`) or 0 (`LOW`).

        """
        pin = self._pins.get(channel)
        if pin:
            return pin.state
        else:
            return None

    def set_pin_key_from_channel(self, channel, key):
        """Set a :class:`Pin`\'s key from a given channel.

        A :class:`Pin` is retrieved based on a given channel, then its
        :attr:`key` is set with `key`.

        Parameters
        ----------
        channel : int
            GPIO channel number associated with the :class:`Pin` whose key will
            be set.
        key : str
            The new key that a :class:`Pin` will be updated with.

        Returns
        -------
        retval : bool
            Returns `True` if the :class:`Pin` was successfully set with `key`.
            Otherwise, it returns `False`.

        """
        pin = self.get_pin_from_channel(channel)
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

    def set_pin_state_from_channel(self, channel, state):
        """Set a :class:`Pin`\'s state from a given channel.

        A :class:`Pin` is retrieved based on a given channel, then its
        :attr:`state` is set with `state`.

        Parameters
        ----------
        channel : int
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
        pin = self.get_pin_from_channel(channel)
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
            The key associated with the :class:`Pin` whose state will be set.
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
    key_to_channel_map : dict
        A dictionary that maps keyboard keys (:obj:`string`) to GPIO channel
        numbers (:obj:`int`). By default, it takes the keys and values defined
        in :mod:`SimulRPi.mapping`'s keymap ``default_key_to_channel_map``.
    channel_to_key_map : dict
        The reverse dictionary of :attr:`key_to_channel_map`. It maps channels
        to keys.
    nb_prints : int
        Number of times the displaying thread :attr:`th_display_leds` has
        printed blinking circles on the terminal. It is used when debugging the
        displaying thread.
    th_display_leds : threading.Thread
        Thread responsible for displaying small blinking circles on the
        terminal as to simulate LEDs connected to an RPi.
    th_listener : threading.Thread
        Thread responsible for listening on any pressed or released key as to
        simulate push buttons connected to an RPi.
    """
    def __init__(self):
        # TODO: remove start_threads
        """
        start_threads: bool
            Whether to eventually start the threads. This flag is set to `True`
            when the function :meth:`setup()` is first called. The default value
            is `False`.
        """
        # self.start_threads = False
        self.mode = None
        self.warnings = True
        self.enable_printing = True
        self.pin_db = PinDB()
        self.key_to_channel_map = copy.copy(default_key_to_channel_map)
        self.channel_to_key_map = {v: k for k, v in
                                   self.key_to_channel_map.items()}
        self._output_channels = []
        self.nb_prints = 0
        self._leds = None
        self.th_display_leds = threading.Thread(name="thread_display_leds",
                                                target=self.display_leds,
                                                args=())
        self.th_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.th_listener.name = "thread_listener"

    def add_pin(self, channel, gpio_function, pull_up_down=None, initial=None):
        """Add an input or output pin to the pin database.

        An instance of :class:`Pin` is created with the given arguments and
        added to the pin database :class:`PinDB`.

        Parameters
        ----------
        channel : int
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
            # Get key associated with the INPUT pin (button)
            # TODO: raise exception if key not found
            key = self.channel_to_key_map.get(channel)
        elif gpio_function == OUT:
            # No key since it is an OUTPUT pin (e.g. LED)
            # Save the channel so the thread that displays LEDs knows what
            # channels are OUTPUT and therefore connected to LEDs.
            self._output_channels.append(channel)
        self.pin_db.create_pin(channel, gpio_function,
                               key=key,
                               pull_up_down=pull_up_down,
                               initial=initial)

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
        while getattr(th, "do_run", True):
            self._leds = ""
            last_msg_length = len(self._leds) if self._leds else 0
            # for channel in sorted(self.channel_output_state_map):
            for channel in self._output_channels:
                pin = self.pin_db.get_pin_from_channel(channel)
                # TODO: pin could be None
                if pin.state == HIGH:
                    # led = "\033[31mo\033[0m"
                    led = '\033[1;31;48m' + 'o' + '\033[1;37;0m'
                else:
                    led = 'o'
                self._leds += led + ' [{}]   '.format(channel)
            if self.enable_printing:
                # If no spaces after the red o's representing the LEDs, then if
                # you press tab or down, it will mess up the display to the right
                print(' ' * last_msg_length, end='\r')
                # print(self._leds, end='\r')
                # TODO: use _add_spaces... and explain
                print('  {}                                         '.format(self._leds), end="\r")
                # sys.stdout.flush()
            self.nb_prints += 1
        if self.enable_printing and self._leds:
            print('  {}                                             '.format(self._leds))
        # logger.debug("Stopping thread: {}()".format(self.display_leds.__name__))
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

            If a key is associated to a channel that is already taken by
            another key, both keys' channels will be swapped. However, if a key
            is being linked to a :obj:`None` channel, then it will take on the
            maximum channel number available + 1.

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
        for keych in key_channels:
            key = keych[0]
            channel = keych[1]
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
    # setprinting(False)
    # Show cursor again
    os.system("tput cnorm ")
    # NOTE: code not used anymore. To be removed
    # Wait a little bit to give the displaying thread a little bit of time to
    # display something but no more than 0.3 seconds
    """
    start = time.time()
    while manager.nb_prints == 0:
        if time.time() - start > 0.3:
            break
    """
    # Check if displaying thread is alive. If the user didn't setup any output
    # channels for LEDs, then the displaying thread was never started
    if manager.th_display_leds.is_alive():
        manager.th_display_leds.do_run = False
        manager.th_display_leds.join()
        logger.debug("Thread stopped: {}".format(manager.th_display_leds.name))
    # Check if listener thread is alive. If the user didn't setup any input
    # channels for buttons, then the listener thread was never started
    if manager.th_listener.is_alive():
        logger.debug("Stopping thread: {}".format(manager.th_listener.name))
        manager.th_listener.stop()
        manager.th_listener.join()
        logger.debug("Thread stopped: {}".format(manager.th_listener.name))
    # Reset Manager's attributes
    # TODO: necessary to so?
    del manager
    manager = Manager()


def input(channel):
    """Read the value of a GPIO pin.

    Parameters
    ----------
    channel : int
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
    # TODO: remove start_threads
    """
    if manager.start_threads and \
    """
    # Start the listener thread only if it not already alive
    if not manager.th_listener.is_alive():
        manager.th_listener.start()
    return manager.pin_db.get_pin_state(channel)


# TODO: output to several channels, see https://bit.ly/2Dgk2Uf
def output(channel, state):
    """Set the output state of a GPIO pin.

    Parameters
    ----------
    channel : int
        Output GPIO channel number based on the numbering system you have
        specified (`BOARD` or `BCM`).
    state : int
        State of the GPIO channel: 1 (`HIGH`) or 0 (`LOW`).


    .. note::

        The displaying thread (for showing "LEDs" on the terminal) is started
        if it is not alive, i.e. it is not already running.

    """
    manager.pin_db.set_pin_state_from_channel(channel, state)
    # TODO: remove start_threads
    """
    if manager.start_threads and \
    """
    # Start the displaying thread only if it not already alive
    if not manager.th_display_leds.is_alive():
        manager.th_display_leds.start()
    # TODO: remove the following
    """
    except RuntimeError as e:
        # This happens when this function is called while the `th_display_leds`
        # thread is being killed in the main thread. is_alive() returns False
        # since the thread was killed and then it is being started once again.
        # By catching this RuntimeError, we give time to the main thread to
        # exit gracefully without this function crashing the program.
        # TODO: might not happen anymore with check on thread is None
        logger.debug(e)
    """


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
    # TODO: remove start_threads
    # manager.start_threads = True
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
