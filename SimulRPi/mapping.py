"""Module that defines the :ref:`dictionary <content-default-keymap-label>`
that  maps keys and GPIO channels.

This module defines the default mapping between keyboard keys and GPIO
channels. It is used by :mod:`GPIO` when monitoring the keyboard with the
package `pynput`_ for any pressed/released key as to simulate a push button
connected to a Raspberry Pi.

Notes
-----
In early RPi models, there are 17 GPIO channels and in late RPi models, there
are 28 GPIO channels.

By default, 28 GPIO channels (from 0 to 27) are mapped to alphanumeric and
special keys. See the :ref:`content of the default keymap
<content-default-keymap-label>`.

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

    * :meth:`GPIO.setkeymap` allows you to modify the default keymap.

    * The keys for the default keymap :attr:`default_key_to_channel_map` must \
    be strings and their values (the channels) should be integers.

.. _pynput: https://pynput.readthedocs.io/en/latest/index.html
.. _pynput reference: https://pynput.readthedocs.io/en/latest/keyboard.html#pynput.keyboard.Key

"""
from SimulRPi.default_keymap import default_key_to_channel_map


# Reverse keymap: channel to key
default_channel_to_key_map = {v: k for k, v in
                              default_key_to_channel_map.items()}
