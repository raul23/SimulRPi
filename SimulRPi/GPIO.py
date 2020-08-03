"""Module that partly fakes `RPi.GPIO`_ and simulates some I/O devices.

It simulates these I/O devices connected to a Raspberry Pi:

    - push buttons by listening to keys pressed/released on the keyboard and
    - LEDs by displaying small dots blinking on the terminal along with their \
    GPIO pin number.

When a LED is turned on, it is shown as a small red circle on the terminal. The
package `pynput`_ is used to monitor the keyboard for any key pressed.

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
    functions from `RPi.GPIO`_. Thus, `let me know through pull requests`_ if
    you want me to add more things to this mock library.

.. _Darth-Vader-RPi project: https://github.com/raul23/Darth-Vader-RPi
.. _let me know through pull requests: https://github.com/raul23/SimulRPi/pulls
.. _pynput: https://pynput.readthedocs.io/en/latest/index.html
.. _RPi.GPIO: https://pypi.org/project/RPi.GPIO/
.. _RPi.GPIO wiki: https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/

"""
import logging
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
            return self._pins.get(channel).state
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

    Attributes
    ----------
    gpio_function : int, None
            Function of a GPIO channel: 1 (`GPIO.INPUT`) or 0 (`GPIO.OUTPUT`).
            Default value is :obj:`None`.
    warnings : bool
        Whether to show warnings when using a pin other than the default GPIO
        function (input). Default value is `True`.
    enable_printing : bool
        Whether to enable printing on the terminal. Default value is `True`.
    pin_db : PinDB
        A :class:`Pin` database. See :class:`PinDB` on how to access it.
    display_th : threading.Thread
        Thread responsible for displaying blinking dots on the terminal as to
        simulate LEDs turning on/off on the RPi.
    listener : threading.Thread
        Thread responsible for listening on any pressed or released key as to
        simulate push buttons on the RPi.
    """
    def __init__(self):
        self.gpio_function = None
        self.warnings = True
        self.enable_printing = True
        self.pin_db = PinDB()
        self._key_to_channel_map = default_key_to_channel_map
        self._channel_to_key_map = {v: k for k, v in
                                    self._key_to_channel_map.items()}
        self._ouput_channels = []
        self.display_th = threading.Thread(target=self.display_leds, args=())
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()

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
            key = self._channel_to_key_map.get(channel)
        elif gpio_function == OUT:
            # No key since it is an OUTPUT pin (e.g. LED)
            # Save the channel so the thread that displays LEDs knows what
            # channels are OUTPUT and therefore connected to LEDs.
            self._ouput_channels.append(channel)
        self.pin_db.create_pin(channel, gpio_function,
                               key=key,
                               pull_up_down=pull_up_down,
                               initial=initial)

    def display_leds(self):
        """Simulate LEDs on a RPi by blinking small dots on a terminal.

        In order to simulate LEDs turning on/off on a RPi, small dots are
        blinked on the terminal along with their GPIO pin number.

        When a LED is turned on, it is shown as a small red circle on the
        terminal.

        .. highlight:: none

        **Example: terminal output** ::

            o [11]   o [9]   o [10]

        .. highlight:: python

        where each circle represents a LED (here they are all turned off) and
        the number between brackets is the associated GPIO pin number.

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
        if self.enable_printing:
            print()
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            leds = ''
            # for channel in sorted(self.channel_output_state_map):
            for channel in self._ouput_channels:
                if self.pin_db.get_pin_from_channel(channel).state == HIGH:
                    led = "\033[31mo\033[0m"
                else:
                    led = 'o'
                leds += led + ' [{}]   '.format(channel)
            if self.enable_printing:
                # TODO: if no spaces after LEDs, then if you press tab or down,
                # it will mess up the display to the right
                print('  {}     \r'.format(leds), end="")
        logger.info("Stopping thread: {}()".format(self.display_leds.__name__))

    @staticmethod
    def get_key_name(key):
        """Get the name of a key as a string.

        The name of the special or alphanumeric key is given by the package
        `pynput`_.

        Parameters
        ----------
        key : pynput.keyboard.Key or pynput.keyboard.KeyCode
            The key (from :mod:`pynput.keyboard`) whose name will be returned.

        Returns
        -------
        key_name : str or None
            Returns the name of the given key if one was found by `pynput`_.
            Otherwise, it returns :obj:`None`.

        """
        if hasattr(key, 'char'):
            # Alphanumeric key
            key_name = key.char
        elif hasattr(key, 'name'):
            # Special key
            key_name = key.name
        else:
            # Unknown key
            key_name = None
        return key_name

    def on_press(self, key):
        """When a valid key is pressed, set its state to `GPIO.LOW`.

        Callback invoked from the thread :attr:`GPIO.Manager.listener`.

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
        """When a valid key is released, set its state to `GPIO.HIGH`.

        Callback invoked from the thread :attr:`GPIO.Manager.listener`.

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
            Dictionary that maps keys to their new GPIO channels.

            **For example**::

                "key_to_channel_map":
                {
                    "f": 24,
                    "g": 25,
                    "h": 23
                }

        """
        # TODO: assert keys (str) and channels (int)
        # TODO: test uniqueness in channel numbers of new map
        assert len(set(new_keymap.values())) == len(new_keymap)
        orig_keych = {}
        for key1, new_ch in new_keymap.items():
            old_ch = self._key_to_channel_map.get(key1)
            # Case 1: if key's channel is not found, maybe it is a special key
            # or an alphanum not already in the keymap
            # Validate the key before updating the keymaps
            if old_ch is None and not self.validate_key(key1):
                # Invalid key: the key is neither a special nor an alphanum key
                orig_keych.setdefault(key1, None)
                raise LookupError("The key '{}' is invalid: only special and "
                                  "alphanum keys are accepted".format(key1))
            key2 = self._channel_to_key_map.get(new_ch)
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
                self._update_keymaps_and_pin_db(
                    key_channels=[(key1, new_ch), (key2, old_ch)])
        if orig_keych:
            # There were updates and/or there are invalid keys
            msg = "Update of Key-to-Channel Map:\n"
            for key, old_ch in orig_keych.items():
                new_ch = self._key_to_channel_map.get(key)
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

        * the two semi-private keymaps :obj:`_key_to_channel_map` and \
        :obj:`_channel_to_key_map`
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
            self._key_to_channel_map[key] = channel
            self._channel_to_key_map[channel] = key
            self.pin_db.set_pin_key_from_channel(channel, key)


manager = Manager()


def cleanup():
    """Clean up any resources (e.g. GPIO channels).

    At the end of any program, it is good practice to clean up any resources
    you might have used. This is no different with `RPi.GPIO`_. By returning
    all channels you have used back to inputs with no pull up/down, you can
    avoid accidental damage to your RPi by shorting out the pins.
    [`RPi.GPIO wiki`_]

    Also, the two threads responsible for displaying "LEDs" on the terminal and
    listening for pressed/released keys are stopped.

    .. note::

        * It will only clean up GPIO channels that your script has used
        * It will also clears the pin numbering system in use (`BOARD` or `BCM`)

        **Ref.:** `RPi.GPIO wiki`_

    """
    manager.display_th.do_run = False
    manager.display_th.join()
    manager.listener.stop()


def input(channel):
    """Read the value of a GPIO pin.

    Parameters
    ----------
    channel : int
        GPIO channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).

    Returns
    -------
    state : int or :obj:`None`
        If no :class:`Pin` could be retrieved based on the given channel
        number, then :obj:`None` is returned. Otherwise, the :class:`Pin`\'s
        state is returned: 1 (`HIGH`) or 0 (`LOW`).

    """
    return manager.pin_db.get_pin_state(channel)


# TODO: output to several channels, see https://bit.ly/2Dgk2Uf
def output(channel, state):
    """Set the output state of a GPIO pin.

    Parameters
    ----------
    channel : int
        GPIO channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).
    state : int
        State of the GPIO channel: 1 (`HIGH`) or 0 (`LOW`).

    """
    manager.pin_db.set_pin_state_from_channel(channel, state)
    try:
        if not manager.display_th.is_alive():
            manager.display_th.start()
    except RuntimeError as e:
        # This happens when this function is called while the `display_th`
        # thread is being killed in the main thread. is_alive() returns False
        # since the thread was killed and then it is being started once again.
        # By catching this RuntimeError, we give time to the main thread to
        # exit gracefully without this function crashing the program.
        logger.debug(e)


def setkeymap(key_to_channel_map):
    """Set the keymap dictionary with new keys and channels.

    The default dictionary :obj:`default_key_to_channel_map` (defined in
    :mod:`SimulRPi.mapping` that maps keys from the keyboard to GPIO channels
    can be modified by providing your own mapping :obj:`key_to_channel_map`
    containing only the keys and channels that you want to be modified.

    Parameters
    ----------
    key_to_channel_map : dict
        A dictionary mapping keys and GPIO channels that will be used to update
        the default keymap found in :mod:`SimulRPi.mapping`.

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
    """Set the numbering system used to identify the IO pins on a RPi within
    `RPi.GPIO`.

    There are two ways of numbering the IO pins on a Raspberry Pi within
    `RPi.GPIO`:

    1. The `BOARD` numbering system: refers to the pin numbers on the P1 header
       of the Raspberry Pi board
    2. The `BCM` numbers: refers to the channel numbers on the Broadcom SOC.

    Parameters
    ----------
    mode : int
        Numbering system used to identify the IO pins on a RPi: `Board` or
        `BCM`.

    References
    ----------
    Function description and more info from `RPi.GPIO wiki`_.

    """
    manager.mode = mode


def setprinting(enable_printing):
    """Enable printing on the terminal.

    If printing is enabled, blinking red dots will be shown on the terminal,
    simulating LEDs on a Raspberry Pi. Otherwise, nothing will be printed on
    the terminal.

    Parameters
    ----------
    enable_printing : bool
        Whether to enable printing on the terminal.

    """
    # TODO: stop thread too?
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
    `RPi.GPIO` wiki: https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/

    """
    manager.add_pin(channel, gpio_function, pull_up_down, initial)


def setwarnings(show_warnings):
    """Set warnings when configuring a GPIO pin other than the default
    (input).

    It is possible that you have more than one script/circuit on the GPIO of
    your Raspberry Pi. As a result of this, if RPi.GPIO detects that a pin has
    been configured to something other than the default (input), you get a
    warning when you try to configure a script. [`RPi.GPIO wiki`_]

    Parameters
    ----------
    show_warnings : bool
        Whether to show warnings when using a pin other than the default GPIO
        function (input).

    """
    manager.warnings = show_warnings
