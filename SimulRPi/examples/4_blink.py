#!/usr/script/env python
"""Example 4: blink a LED for 4 seconds

This script allows you to blink a LED on channel 20 for 4 seconds (or until you
press :obj:`ctrl` + :obj:`c`).

The script can be run on a Raspberry Pi (RPi) or on your computer in which case
it will make use of the mocK library `SimulRPi
<https://github.com/raul23/SimulRPi>`_.

Usage
-----

Run the script on the RPi::

    $ 4_blink_py

Run the script on your computer (simulation flag)::

    $ 4_blink_py -s

"""
import time
GPIO = None


def blink_led(channel):
    """Blink a LED on the terminal for 4 seconds

    The led is turned on and off for 0.5 seconds, respectively.

    Press :obj:`ctrl` + :obj:`c` to stop the blinking and exit from the
    function.

    Parameters
    ----------
    channel : int
        GPIO channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).

    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.OUT)
    start = time.time()
    while (time.time() - start) < 4:
        try:
            GPIO.output(channel, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(channel, GPIO.LOW)
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
    GPIO.cleanup()


if __name__ == '__main__':
    if args.simulation:
        import SimulRPi.GPIO as GPIO
        print("Simulation mode enabled")
    else:
        import RPi.GPIO as GPIO
    blink_led(20)
