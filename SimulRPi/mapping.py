"""Module that defines a dictionary that maps keys and GPIO channels.

This module defines the default mapping between keyboard keys and GPIO
channels. It is used by :mod:`GPIO` when monitoring the keyboard with the
package `pynput`_ for any pressed/released key as to simulate a push button
connected to a Raspberry Pi.

Notes
-----
In early RPi models, there are 17 GPIO channels and in late RPi models, there
are 28 GPIO channels.

By default, 28 GPIO channels (from 0 to 27) are mapped to alphanumeric and
special keys.

Here is the full list of special keys you can use with info about some of them
(taken from `pynput reference`_):

    - :obj:`alt`
    - :obj:`alt_gr`
    - :obj:`alt_l`
    - :obj:`alt_r`
    - :obj:`backspace`
    - :obj:`caps_lock`
    - :obj:`cmd`: A generic command button. On PC platforms, this corresponds to
      the Super key or Windows key, and on Mac it corresponds to the Command key.
    - :obj:`cmd_l`: The left command button. On PC platforms, this corresponds
      to the Super key or Windows key, and on Mac it corresponds to the Command
      key.
    - :obj:`cmd_r`: The right command button. On PC platforms, this corresponds
      to the Super key or Windows key, and on Mac it corresponds to the Command key.
    - :obj:`ctrl`: A generic Ctrl key.
    - :obj:`ctrl_l`
    - :obj:`ctrl_r`
    - :obj:`delete`
    - :obj:`down`
    - :obj:`end`
    - :obj:`enter`
    - :obj:`esc`
    - :obj:`f1`: The function keys. F1 to F20 are defined.
    - :obj:`home`
    - :obj:`insert`: The Insert key. This may be undefined for some platforms.
    - :obj:`left`
    - :obj:`media_next`
    - :obj:`media_play_pause`
    - :obj:`media_previous`
    - :obj:`media_volume_down`
    - :obj:`media_volume_mute`
    - :obj:`media_volume_up`
    - :obj:`menu`: The Menu key. This may be undefined for some platforms.
    - :obj:`num_lock`: The NumLock key. This may be undefined for some platforms.
    - :obj:`page_down`
    - :obj:`page_up`
    - :obj:`pause`: The Pause/Break key. This may be undefined for some platforms.
    - :obj:`print_screen`: The PrintScreen key. This may be undefined for some
      platforms.
    - :obj:`right`
    - :obj:`scroll_lock`
    - :obj:`shift`
    - :obj:`shift_l`
    - :obj:`shift_r`
    - :obj:`space`
    - :obj:`tab`
    - :obj:`up`

References
----------
- **RPi Header**: https://bit.ly/30ZM2Uj
- **pynput**: https://pynput.readthedocs.io/

.. important::

    * :meth:`GPIO.setkeymap` allows you to modify this default keymap.

    * The keys for the default dictionary :attr:`default_key_to_channel_map` \
    must be strings and their values (the channels) should be integers.

.. _pynput: https://pynput.readthedocs.io/en/latest/index.html
.. _pynput reference: https://pynput.readthedocs.io/en/latest/keyboard.html#pynput.keyboard.Key

"""
# from SimulRPi.utils import convert_keys_to_int


# TODO: specify in docs that key must be a string even if key is a numeric key
# [start-section]
default_key_to_channel_map = {
    "0": 0,  # sudo on mac
    "1": 1,  # sudo on mac
    "2": 2,  # sudo on mac
    "3": 3,  # sudo on mac
    "4": 4,  # sudo on mac
    "5": 5,  # sudo on mac
    "6": 6,  # sudo on mac
    "7": 7,  # sudo on mac
    "8": 8,  # sudo on mac
    "9": 9,  # sudo on mac
    "q": 10,  # sudo on mac
    "alt": 11,  # left alt on mac
    "alt_l": 12,  # not recognized on mac
    "alt_r": 13,
    "alt_gr": 14,
    "cmd": 15,  # left cmd on mac
    "cmd_l": 16,  # not recognized on mac
    "cmd_r": 17,
    "ctrl": 18,  # left ctrl on mac
    "ctrl_l": 19,  # not recognized on mac
    "ctrl_r": 20,
    "media_play_pause": 21,
    "media_volume_down": 22,
    "media_volume_mute": 23,
    "media_volume_up": 24,
    "shift": 25,  # left shift on mac
    "shift_l": 26,  # not recognized on mac
    "shift_r": 27,
}
# [end-section]

# TODO: necessary conversion?
# default_key_to_channel_map = convert_keys_to_int(default_key_to_channel_map)
default_channel_to_key_map = {v: k for k, v in
                              default_key_to_channel_map.items()}
