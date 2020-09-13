===============================
Test threads raising exceptions
===============================
We will show cases where the displaying and listening threads raise their own
exceptions instead of relying on the main program to do it for them.

These displaying and listening threads are defined in
``SimulRPi.manager.DisplayExceptionThread`` and
``SimulRPi.manager.KeyboardExceptionThread``, respectively.

As their names suggest, the display thread is responsible for displaying LEDs
in the terminal and the listening thread monitors the keyboard for any pressed
key. They are used to simulate I/O devices connected to a Raspberry Pi.

Case 1: the displaying thread raises its own exception
======================================================
Prepare the setup:

1. ``DisplayExceptionThread.run()`` is modified so as to raise an exception when
   the displaying thread's target function raises one:

   .. code-block:: python

      def run(self):
          try:
            self._target(*self._args, **self._kwargs)
          except Exception as e:
              self.exc = e
              raise e

2. ``SimulRPi.GPIO.output()`` is modified as to comment the call to
   ``SimulRPi.GPIO._raise_if_thread_exception()`` at the end of the function.

   Thus, we don't want ``output()`` to raise an exception anymore, since the
   thread is now responsible for doing it in its ``run`` method.

3. We will raise a ``ZeroDivisionError`` exception in
   ``SimulRPi.manager.display_leds()`` by adding ``test = 1/0`` in the method.

We run the ``darth_vader_rpi.start_dv`` script which is part of the
installation of the `Darth-Vader-RPi`_ library::

   $ start_dv -s

**Result**:
* ``ZeroDivisionError`` exception is raised but is not caught by the main program
(more specifically in the ``except block`` at the end of
``darth_vader_rpi.darth_vader.activate()``)
* The display of LEDs in the terminal is not working because the displaying
thread is dead
* The listening thread is still working and therfore you can press keys to
play sounds: lightsaber sound effects, Darth Vader's theme song and quotes.

Case 2: the listening thread raises its own exception
=====================================================

.. URLs
.. external links
.. _Darth-Vader-RPi: https://github.com/raul23/Darth-Vader-RPi

