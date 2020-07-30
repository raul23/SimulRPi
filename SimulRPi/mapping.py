"""Module that defines a dictionary that maps keys and GPIO channels.

This module defines the default mapping between keys from the keyboard and GPIO
channels. It is used by the module :mod:`GPIO`.

Notes
-----
28 GPIO channels (from GPIO-0 to GPIO-27) are mapped to keys (numbers [0-9] and
letters following the qwerty order).

In early RPi models, there are 17 GPIO channels and in late RPi models, there
are 28 GPIO channels.

References
----------
RPi GPIO Header: https://bit.ly/30ZM2Uj

.. important::

    :meth:`GPIO.setkeymap` allows you to modify this default keymap.

"""

default_key_channel_mapping = {
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "q": 10,
    "w": 11,
    "e": 12,
    "r": 13,
    "t": 14,
    "y": 15,
    "u": 16,
    "i": 17,
    "o": 18,
    "p": 19,
    "a": 20,
    "s": 21,
    "d": 22,
    "f": 23,
    "g": 24,
    "h": 25,
    "j": 26,
    "k": 27
}
