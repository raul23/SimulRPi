=============
API Reference
=============

.. contents::
   :depth: 2
   :local:

:mod:`SimulRPi.GPIO`
====================

.. automodule:: SimulRPi.GPIO
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`SimulRPi.manager`
=======================

.. automodule:: SimulRPi.manager
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`SimulRPi.mapping`
=======================

.. automodule:: SimulRPi.mapping
   :members:
   :undoc-members:
   :show-inheritance:

.. _content-default-keymap-label:

**Content of the default keymap dictionary** (*key:* keyboard key as
:obj:`string`, *value:* GPIO channel as :obj:`int`):

.. literalinclude:: ../SimulRPi/default_keymap.py
   :language: Python
   :end-before: [end-section]

.. _important-platform-limitations-label:

.. important::

   There are some platform limitations on using some of the keyboard keys with
   `pynput <https://pynput.readthedocs.io/>`__ which is used for monitoring the
   keyboard.

   For instance, on macOS, some keyboard keys may require that you run your
   script with `sudo`. All alphanumeric keys and some special keys
   (e.g. :obj:`backspace` and :obj:`right`) require `sudo`. In the content of
   :ref:`default_key_to_channel_map <content-default-keymap-label>` shown
   previously, I commented those keyboard keys that need `sudo` on macOS. The
   others don't need `sudo` on macOS such as :obj:`cmd_r` and :obj:`shift`.

   For more information about those platform limitations, see
   `pynput documentation`_.

.. warning::

   If you want to be able to run your python script with `sudo` in order to use
   some keys that require it, you might need to edit **/etc/sudoers** to add
   your :obj:`PYTHONPATH` if your script makes use of your :obj:`PYTHONPATH` as
   configured in your `~/.bashrc` file. However, I don't recommend editing
   **/etc/sudoers** since you might break your `sudo` command (e.g.
   ``sudo: /etc/sudoers is owned by uid 501, should be 0``).

   Instead, use the keys that don't requre `sudo` such as :obj:`cmd_r` and
   :obj:`shift` on macOS.

.. note::

   On macOS, if the left keys :obj:`alt_l`, :obj:`ctrl_l`, :obj:`cmd_l`, and
   :obj:`shift_l` are not recognized, use their generic counterparts instead:
   :obj:`alt`, :obj:`ctrl`, :obj:`cmd`, and :obj:`shift`.

:mod:`SimulRPi.pinbdb`
======================

.. automodule:: SimulRPi.pindb
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`SimulRPi.run\_examples`
=============================

.. automodule:: SimulRPi.run_examples
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`SimulRPi.utils`
=====================

.. automodule:: SimulRPi.utils
   :members:
   :undoc-members:
   :show-inheritance:

.. URLs
.. external links
.. _pynput documentation: https://pynput.readthedocs.io/en/latest/limitations.html
