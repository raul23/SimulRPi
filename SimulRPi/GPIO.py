"""Module that partly mocks `RPi.GPIO`_ and simulates some I/O devices.

It simulates these I/O devices connected to a Raspberry Pi:

    - push buttons by listening to keys pressed/released on the keyboard and
    - LEDs by displaying small dots blinking on the terminal along with their \
    GPIO pin number.

When a LED is turned on, it is shown as a small red circle on the terminal. The
package `pynput`_ is used to monitor the keyboard for any key pressed.

.. highlight:: none

**Example: terminal output** ::

    o [11]   o [9]   o [10]

where each circle represents a LED (here they are all turn off) and the number
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

from SimulRPi.mapping import default_key_channel_mapping

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
        GPIO channel number.
    gpio_function : int
        Function of a GPIO channel: 1 (`GPIO.INPUT`) or 0 (`GPIO.OUTPUT`).
    key : str or None, optional
        Key associated with the GPIO channel, e.g. "g".
    pull_up_down : int or None, optional
        Initial value of an input channel, e.g. `GPIO.PUP_UP`.
    initial : int or None, optional
        Initial value of an output channel, e.g. `GPIO.HIGH`.

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

        The dictionary (a "database" of :class:`GPIO.Pin`\s) must be accessed
        through the different methods available in :class:`PinDB`, e.g.
        :meth:`get_pin_from_channel`.

    """
    def __init__(self):
        self._pins = {}
        # Only INPUT keys
        # TODO: explain more
        self._key_to_pin_map = {}

    def create_pin(self, channel, gpio_function, key=None, pull_up_down=None,
                   initial=None):
        """Instantiate :class:`GPIO.Pin` and save it in a dictionary.

        Based on the given parameters, an instance of :class:`GPIO.Pin` is
        created and added to a dictionary.

        Parameters
        ----------
        channel : int
            GPIO channel number.
        gpio_function : int
            Function of a GPIO channel: 1 (`GPIO.INPUT`) or 0 (`GPIO.OUTPUT`).
        key : str or None, optional
            Key associated with the GPIO channel, e.g. "g".
        pull_up_down : int or None, optional
        initial : int or None, optional
            Initial value of an output channel, e.g. `GPIO.HIGH`.

        """
        self._pins[channel] = Pin(channel, gpio_function, key, pull_up_down,
                                  initial)
        if key:
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
            If no :class:`Pin` could be retrieved based on a channel,
            :obj:`None` is returned.

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
            If no :class:`Pin` could be retrieved based on a pressed/released
            key, :obj:`None` is returned.

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
        new_key : str
            The new key that a :class:`Pin` will be updated with.

        Returns
        -------
        retval : bool
            Returns True if the :class:`Pin` was successfully set with `key`.
            Otherwise, it returns False.

        """
        pin = self.get_pin_from_channel(channel)
        if pin:
            old_key = pin.key
            pin.key = key
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
            State of the GPIO channel: 1 (`HIGH`) or 0 (`LOW`).
        Returns
        -------
        retval : bool
            Returns True if the :class:`Pin` was successfully set with `state`.
            Otherwise, it returns False.

        """
        pin = self.get_pin_from_channel(channel)
        if pin:
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
    gpio_function : int
            Function of a GPIO channel: 1 (`GPIO.INPUT`) or 0 (`GPIO.OUTPUT`).
    warnings : bool

    enable_printing : bool

    pin_db : PinDB

    display_th : threading.Thread

    listener : threading.Thread

    """
    def __init__(self):
        # import ipdb
        # ipdb.set_trace()
        self.gpio_function = None
        self.warnings = True
        self.enable_printing = True
        self.pin_db = PinDB()
        self._key_channel_map = default_key_channel_mapping
        self._channel_key_map = {v: k for k, v in self._key_channel_map.items()}
        self._ouput_channels = []
        self.display_th = threading.Thread(target=self.display_leds, args=())
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()

    def add_pin(self, channel, gpio_function, pull_up_down=None, initial=None):
        """

        Parameters
        ----------
        channel
        gpio_function
        pull_up_down
        initial

        """
        if gpio_function == IN:
            # Get user-defined key associated with INPUT pin (button)
            # TODO: raise exception if key not found
            key = self._channel_key_map.get(channel)
            self.pin_db.create_pin(channel, gpio_function,
                                   key=key,
                                   pull_up_down=pull_up_down,
                                   initial=initial)
        elif gpio_function == OUT:
            # No key since it is an OUTPUT pin (e.g. LED)
            self.pin_db.create_pin(channel, gpio_function,
                                   pull_up_down=pull_up_down,
                                   initial=initial)
            self._ouput_channels.append(channel)

    def display_leds(self):
        """
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
                print('  {}\r'.format(leds), end="")
        logger.info("Stopping thread: display_leds()")

    def on_press(self, key):
        """

        Parameters
        ----------
        key

        """
        try:
            # print('alphanumeric key {0} pressed'.format(
            #      key.char))
            if str(key.char).isalnum():
                pin = self.pin_db.get_pin_from_key(key.char)
                if pin:
                    pin.state = LOW
        except AttributeError:
            # print('special key {0} pressed'.format(
            #  key))
            pass

    def on_release(self, key):
        """

        Parameters
        ----------
        key

        """
        if key == keyboard.Key.esc:
            # TODO: Stop listener
            return False
        elif hasattr(key, 'char') and str(key.char).isalnum():
            pin = self.pin_db.get_pin_from_key(key.char)
            if pin:
                pin.state = HIGH

    def update_keymap(self, new_map):
        """

        Parameters
        ----------
        new_map

        """
        # TODO: test uniqueness in channel numbers of new map
        assert len(set(new_map.values())) == len(new_map)
        msg = "Update of Key-to-Channel Mapping:\n"
        update_count = 0
        for key, new_ch in new_map.items():
            orig_ch = self._key_channel_map.get(key)
            other_key = self._channel_key_map.get(new_ch)
            if key == other_key and new_ch == orig_ch:
                # No updates
                continue
            else:
                update_count += 1
            self._key_channel_map[other_key] = orig_ch
            self._key_channel_map[key] = new_ch
            msg += 'Key "{}": Channel {} ------> Channel {}\n'.format(
                other_key, new_ch, orig_ch)
            msg += 'Key "{}": Channel {} ------> Channel {}\n'.format(
                key, orig_ch, new_ch)
            self.pin_db.set_pin_key_from_channel(new_ch, key)
            self.pin_db.set_pin_key_from_channel(orig_ch, other_key)
        if update_count:
            logger.info(msg)
            self._channel_key_map = {v: k for k, v in
                                     self._key_channel_map.items()}


manager = Manager()


def cleanup():
    """Clean up any resources (e.g. GPIO channels).

    At the end any program, it is good practice to clean up any resources you
    might have used. This is no different with RPi.GPIO. By returning all
    channels you have used back to inputs with no pull up/down, you can avoid
    accidental damage to your RPi by shorting out the pins. [`RPi.GPIO wiki`_]

    Also, the two threads responsible for displaying "LEDs" on the terminal and
    listening for keys pressed/released are stopped.

    .. note::

        * It will only clean up GPIO channels that your script has used
        * It will also clears the pin numbering system in use (*BOARD* or *BCM*)

        **Ref.:** `RPi.GPIO wiki`_

    """
    manager.display_th.do_run = False
    manager.display_th.join()
    manager.listener.stop()


def input(channel):
    """
    Parameters
    ----------
    channel : int
        GPIO channel number.

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
    """

    Parameters
    ----------
    channel : int
        GPIO channel number.
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
        # exit gracefully without this function crashing anything.
        logger.debug(e)


def setkeymap(key_to_channel_map):
    """

    Parameters
    ----------
    key_to_channel_map

    """
    manager.update_keymap(key_to_channel_map)


def setmode(mode):
    """

    Parameters
    ----------
    mode :

    """
    manager.mode = mode


def setprinting(enable_printing):
    """

    Parameters
    ----------
    enable_printing

    """
    manager.enable_printing = enable_printing


# TODO: setup more than one channel, see https://bit.ly/2Dgk2Uf
def setup(channel, gpio_function, pull_up_down=None, initial=None):
    """

    Parameters
    ----------
    channel : int
        GPIO channel number.
    gpio_function : int
        Function of a GPIO channel: 1 (`GPIO.INPUT`) or 0 (`GPIO.OUTPUT`).
    pull_up_down : int or None, optional
        Initial value of an input channel, e.g. `GPIO.PUP_UP`.
    initial : int or None, optional
        Initial value of an output channel, e.g. `GPIO.HIGH`.

    """
    manager.add_pin(channel, gpio_function, pull_up_down, initial)


def setwarnings(enable_warnings):
    """Set warnings when configuring a GPIO pin other than the default
    (input).

    It is possible that you have more than one script/circuit on the GPIO of
    your Raspberry Pi. As a result of this, if RPi.GPIO detects that a pin has
    been configured to something other than the default (input), you get a
    warning when you try to configure a script. [`RPi.GPIO wiki`_]

    Parameters
    ----------
    enable_warnings : bool
        Whether to enable the warnings when using a pin other than the default
        GPIO function (input).

    """
    manager.warnings = enable_warnings
