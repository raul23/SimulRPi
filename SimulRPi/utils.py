import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    import SimulRPi.GPIO as GPIO


def blink_led(channel, time_on, time_off):
    """Blink one LED.

    A LED on the given `channel` will be turned on and off for `time_one` and
    `time_off` seconds, respectively.

    Parameters
    ----------
    channel
    time_on
    time_off

    """
    turn_on_led(channel)
    time.sleep(time_on)
    turn_off_led(channel)
    time.sleep(time_off)


def turn_off_led(channel):
    """Turn off a LED from a given channel.

    Parameters
    ----------
    channel : int
        Channel number associated with a LED which will be turned off.

    """
    GPIO.output(channel, GPIO.LOW)


def turn_on_led(channel):
    """Turn on a LED from a given channel.

    Parameters
    ----------
    channel : int
        Channel number associated with a LED which will be turned on.

    """
    GPIO.output(channel, GPIO.HIGH)
