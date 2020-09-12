"""Collection of utility functions used for the SimulRPi library.
"""
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    import SimulRPi.GPIO as GPIO


def blink_led(channel, time_led_on, time_led_off):
    """Blink one LED.

    A LED on the given ``channel`` will be turned ON and OFF for ``time_led_on``
    seconds and ``time_led_off`` seconds, respectively.

    Parameters
    ----------
    channel : int or list or tuple
        Channel number associated with a LED which will blink.
    time_led_on : float
        Time in seconds the LED will stay turned ON at a time.
    time_led_off : float
       Time in seconds the LED will stay turned OFF at a time.

    """
    turn_on_led(channel)
    time.sleep(time_led_on)
    turn_off_led(channel)
    time.sleep(time_led_off)


def turn_off_led(channel):
    """Turn off a LED from a given channel.

    Parameters
    ----------
    channel : int or list or tuple
        Channel number associated with a LED which will be turned off.

    """
    GPIO.output(channel, GPIO.LOW)


def turn_on_led(channel):
    """Turn on a LED from a given channel.

    Parameters
    ----------
    channel : int or list or tuple
        Channel number associated with a LED which will be turned on.

    """
    GPIO.output(channel, GPIO.HIGH)
