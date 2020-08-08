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


# TODO: description
def convert_keys_to_int(d: dict):
    # Taken from https://stackoverflow.com/a/62625676
    new_dict = {}
    for k, v in d.items():
        try:
            new_key = int(k)
        except ValueError:
            new_key = k
        if type(v) == dict:
            v = convert_keys_to_int(v)
        new_dict[new_key] = v
    return new_dict


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
