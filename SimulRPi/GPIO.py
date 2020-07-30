"""Module that partly mocks `RPi.GPIO`_ and simulates some I/O devices.

It simulates these I/O devices connected to a Raspberry Pi:

    - push buttons by listening to keys pressed/released on the keyboard and
    - LEDs by displaying small dots blinking on the terminal along with their \
    GPIO pin number.

When a LED is turn on, it is shown as a small red circle on the terminal. The
package `pynput`_ is used to monitor the keyboard for any key pressed.

Example: terminal output
    ``o [11]   o [9]   o [10]``

Where each circle represents a LED (here they are all turn off) and the number
between brackets is the associated GPIO pin number.

.. important::

    This library is not a Raspberry Pi emulator nor a complete simulator of
    `RPi.GPIO`_, only the most important functions that I needed for my
    `Darth-Vader-RPi project`_ were added.

    If there is enough interest in this library, I will eventually mock more
    functions from `RPi.GPIO`_. Thus, `let me know through pull requests`_ if
    you want me to add more things to this mock library.

.. _Darth-Vader-RPi project: https://github.com/raul23/Darth-Vader-RPi
.. _let me know through pull requests: https://github.com/raul23/SimulRPi/pulls
.. _pynput: https://pynput.readthedocs.io/en/latest/index.html
.. _RPi.GPIO: https://pypi.org/project/RPi.GPIO/

"""
import logging
import threading
from logging import NullHandler

from pynput import keyboard

from .mapping import default_key_channel_mapping

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

BCM = 1
HIGH = 1
LOW = 0
IN = 0
OUT = 1
PUD_UP = 1


class Pin:
    """Class that represents a GPIO pin.

    Parameters
    ----------
    channel : int
        GPIO channel number according to the specified numbering system (BOARD or BCM).
    mode : int

    key
    pull_up_down
    initial

    See Also
    --------
    PinDB : Class for storing and accessing :class:`Pin`\s.

    """
    def __init__(self, channel, mode, key=None, pull_up_down=None, initial=None):
        import ipdb
        ipdb.set_trace()
        self.channel = channel
        self.key = key
        self.mode = mode
        self.initial = initial
        self.pull_up_down = pull_up_down
        self.key = key
        if mode == IN:
            self.state = HIGH
        else:
            self.state = LOW


class PinDB:
    """Class for storing and modifying :class:`Pin`\s.

    See Also
    --------
    Pin : Class that represents a GPIO pin.

    """
    def __init__(self):
        self._pins = {}
        # Only INPUT keys
        # TODO: explain more
        self._key_to_pin_map = {}

    def create_pin(self, channel, mode, key=None, pull_up_down=None,
                   initial=None):
        self._pins[channel] = Pin(channel, mode, key, pull_up_down, initial)
        if key:
            self._key_to_pin_map[key] = self._pins[channel]

    def get_pin_from_channel(self, channel):
        return self._pins.get(channel)

    def get_pin_from_key(self, key):
        return self._key_to_pin_map.get(key)

    def get_pin_state(self, channel):
        pin = self._pins.get(channel)
        if pin:
            return self._pins.get(channel).state
        else:
            return None

    def set_pin_key(self, channel, new_key):
        pin = self.get_pin_from_channel(channel)
        if pin:
            old_key = pin.key
            pin.key = new_key
            del self._key_to_pin_map[old_key]
            self._key_to_pin_map[new_key] = pin
            return True
        else:
            return False

    def set_pin_state_from_channel(self, channel, state):
        pin = self.get_pin_from_channel(channel)
        if pin:
            pin.state = state
            return True
        else:
            return False

    def set_pin_state_from_key(self, key, state):
        pin = self.get_pin_from_key(key)
        if pin:
            pin.state = state
            return True
        else:
            return False


class GPIO:
    """
    :class:`pynput.keyboard` is ...  `Test`
    """
    def __init__(self):
        self.mode = None
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

    def add_pin(self, channel, mode, pull_up_down=None, initial=None):
        if mode == IN:
            # Get user-defined key associated with INPUT pin (button)
            # TODO: raise exception if key not found
            key = self._channel_key_map.get(channel)
            self.pin_db.create_pin(channel, mode, key, pull_up_down, initial)
        elif mode == OUT:
            # No key since it is an OUTPUT pin (e.g. LED)
            self.pin_db.create_pin(channel, mode, pull_up_down=pull_up_down,
                                   initial=initial)
            self._ouput_channels.append(channel)

    def display_leds(self):
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
        if key == keyboard.Key.esc:
            # TODO: Stop listener
            return False
        elif hasattr(key, 'char') and str(key.char).isalnum():
            pin = self.pin_db.get_pin_from_key(key.char)
            if pin:
                pin.state = HIGH

    def update_key_to_channel_map(self, new_map):
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
            self.pin_db.set_pin_key(new_ch, key)
            self.pin_db.set_pin_key(orig_ch, other_key)
        if update_count:
            logger.info(msg)
            self._channel_key_map = {v: k for k, v in
                                     self._key_channel_map.items()}


gpio = GPIO()


def cleanup():
    gpio.display_th.do_run = False
    gpio.display_th.join()
    gpio.listener.stop()


def disableprinting():
    gpio.enable_printing = False


def input(channel):
    return gpio.pin_db.get_pin_state(channel)


def output(channel, state):
    gpio.pin_db.set_pin_state_from_channel(channel, state)
    try:
        if not gpio.display_th.is_alive():
            gpio.display_th.start()
    except RuntimeError as e:
        # This happens when this function is called while the `display_th`
        # thread is being killed in the main thread. is_alive() returns False
        # since the thread was killed and then it is being started once again.
        # By catching this RuntimeError, we give time to the main thread to
        # exit gracefully without this function crashing anything.
        logger.debug(e)


def setkeymap(key_to_channel_map):
    gpio.update_key_to_channel_map(key_to_channel_map)


def setmode(mode):
    gpio.mode = mode


# mode = {IN, OUT}
def setup(channel, mode, pull_up_down=None, initial=None):
    gpio.add_pin(channel, mode, pull_up_down, initial)


def setwarnings(mode):
    gpio.warnings = mode
