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
``DisplayExceptionThread.run()`` is modified so as to raise an exception when
the displaying thread's target function raises one:

.. code-block:: python

   def run(self):
       try:
         self._target(*self._args, **self._kwargs)
       except Exception as e:
           self.exc = e
           raise e

``SimulRPi.GPIO.output()`` is modified as to comment the call to
``SimulRPi.GPIO._raise_if_thread_exception()`` at the end of the function.
Thus, we don't want ``output()`` to raise an exception anymore, since the
thread is now responsible for doing in its



Case 2: the listening thread raises its own exception
=====================================================

