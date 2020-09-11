================================
Example: How to use ``SimulRPi``
================================

We will show a code example that makes use of both `SimulRPi.GPIO`_ and
`RPi.GPIO`_ so you can run the script on a Raspberry Pi (RPi) or computer.

.. contents::
   :depth: 2
   :local:

Code example
============
The following code blinks a LED for 3 seconds after a user presses a push
button. The code can be run on an RPi or computer. In the latter case, the
simulation package ``SimulRPi`` is used for displaying a LED in the terminal
and monitoring the keyboard.

.. _script-label:

.. code-block:: python
   :emphasize-lines: 5, 9
   :caption: Script that blinks a LED for 3 seconds when a button (or the
             ``cmd_r`` key) is pressed

    import sys
    import time

    if len(sys.argv) > 1 and sys.argv[1] == '-s':
        import SimulRPi.GPIO as GPIO
        msg1 = "\nPress key 'cmd_r' to blink a LED"
        msg2 = "Key 'cmd_r' pressed!"
    else:
        import RPi.GPIO as GPIO
        msg1 = "\nPress button to blink a LED"
        msg2 = "Button pressed!"

    led_channel = 10
    button_channel = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led_channel, GPIO.OUT)
    GPIO.setup(button_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print(msg1)
    while True:
        try:
            if not GPIO.input(button_channel):
                print(msg2)
                start = time.time()
                while (time.time() - start) < 3:
                    GPIO.output(led_channel, GPIO.HIGH)
                    time.sleep(0.5)
                    GPIO.output(led_channel, GPIO.LOW)
                    time.sleep(0.5)
                break
        except KeyboardInterrupt:
            break
    GPIO.cleanup()

Add the previous code in a script named for example `script.py`. To run it on
your **computer**, use the option ``-s`` like this::

   $ python script.py -s

If you run it on your **RPi**, connect a LED to the GPIO channel 10 and a push
button to the GPIO channel 17. You don't have to add the option ``-s``  when
running the script on the RPi::

   $ python script.py

On your **computer**, you get the following:

.. code-block:: console
   :caption: Output for the script when it is run on a **computer** (blinking
             of the LED not shown)

   $ python script.py -s

   Press key 'cmd_r' to blink a LED
   Key 'cmd_r' pressed!

     🛑  [10]

On your **RPi**, you get almost the same result without the LED shown in the
terminal:

.. code-block:: console
   :caption: Output for the script when it is run on an **RPi**

   $ python script.py

   Press button to blink a LED
   Button pressed!

.. note::

   The script can be stopped at any moment if the keys ``ctrl`` + ``c`` are
   pressed.

Code explanation
================
At the beginning of the `script`_, we check if the flag ``-s`` was used. If it
is the case, then the simulation module :mod:`SimulRPi.GPIO` is imported.
Otherwise, the module ``RPi.GPIO`` is used::

   if len(sys.argv) > 1 and sys.argv[1] == '-s':
      import SimulRPi.GPIO as GPIO
      msg1 = "\nPress key 'cmd_r' to blink a LED"
      msg2 = "Key 'cmd_r' pressed!"
   else:
      import RPi.GPIO as GPIO
      msg1 = "\nPress button to blink a LED"
      msg2 = "Button pressed!"

Then, we setup the LED and button channels using the *BCM* mode::

   led_channel = 10
   button_channel = 17
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(led_channel, GPIO.OUT)
   GPIO.setup(button_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)

Finally, we enter the infinite loop where we wait for the push button (or key
``cmd_r``) to be pressed or ``ctrl`` + ``c`` which terminates the script
immediately. If the push button (or the key ``cmd_r``) is pressed, we blink a
LED for 3 seconds, then do a cleanup of GPIO channels (very important), and
terminate the script:

.. code-block:: python
   :emphasize-lines: 14

   while True:
        try:
            if not GPIO.input(button_channel):
                print(msg2)
                start = time.time()
                while (time.time() - start) < 3:
                    GPIO.output(led_channel, GPIO.HIGH)
                    time.sleep(0.5)
                    GPIO.output(led_channel, GPIO.LOW)
                    time.sleep(0.5)
                break
        except KeyboardInterrupt:
            break
    GPIO.cleanup()

.. URLs
.. external links
.. _RPi.GPIO: https://pypi.org/project/RPi.GPIO/

.. internal links
.. _script: #script-label
.. _SimulRPi.GPIO: api_reference.html#module-SimulRPi.GPIO
