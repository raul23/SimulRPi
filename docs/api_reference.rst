=============
API Reference
=============

.. contents::
   :depth: 2
   :local:


:mod:`SimulRPi.GPIO`
==================================

.. automodule:: GPIO
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`SimulRPi.mapping`
==================================

.. automodule:: SimulRPi.mapping
   :members:
   :undoc-members:
   :show-inheritance:

**Content of the default keymap dictionary** (*key:* key from keyboard, *value:* GPIO channel):

.. literalinclude:: ../SimulRPi/mapping.py
   :language: Python
   :start-after: [start-section]
   :end-before: [end-section]

.. important::

   There are some platform limitations on using some of the keyboard keys with
   ``pynput``. For instance, on macOS some keys may require that you run your
   script as root with `sudo`. All alphanumeric keys and some special keys
   (:obj:`backspace` and :obj:`right`) require `sudo`. In the previous list,
   I commented those keys that need `sudo` on macOS. The others don't need
   `sudo` on macOS such as :obj:`cmd_r` and :obj:`shift`.

   For more information about those limitations, see `pynput
   documentation <https://pynput.readthedocs.io/en/latest/limitations.html>`_.

.. warning::

   If you want to be able to run your python script with `sudo` in order to use
   some keys that require it, you might need to edit **/etc/sudoers** to add
   your :obj:`PYTHONPATH` if your script makes use of your :obj:`PYTHONPATH` as
   setup in the `~/.bashrc` file. However, I don't recommend editing
   **/etc/sudoers** since you might break your `sudo` command (e.g.
   ``sudo: /etc/sudoers is owned by uid 501, should be 0``).

   Instead, use the keys that don't requre `sudo` such as :obj:`cmd_r` and
   :obj:`shift` on macOS.

.. note::

   On macOS, the left keys :obj:`alt_l`, :obj:`ctrl_l`, :obj:`cmd_l`, and
   :obj:`shift_l` are not recognized. Use their generic counterparts instead:
   :obj:`alt`, :obj:`ctrl`, :obj:`cmd`, and :obj:`shift`.

:mod:`SimulRPi.run\_examples`
==================================

.. automodule:: run_examples
   :members:
   :undoc-members:
   :show-inheritance:
