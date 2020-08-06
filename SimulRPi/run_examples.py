#!/usr/script/env python
"""Script for executing examples on a Raspberry Pi or computer (simulation).

This script allows you to run different code examples on your Raspberry Pi (RPi)
or computer in which case it will make use of the mock library `SimulRPi`_.

The code examples test different parts of the mock library `SimulRPi`_ in order
to show what it is capable of simulating from a RPi:

    * Turn on/off LEDs
    * Detect pressed keys and perform an action

Usage
-----

Once the `SimulRPi` package is `installed`_, you should have access to
the :mod:`start_dv` script:

    ``run_examples [-h] [-v] -e EXAMPLE_NUMBER [-s]``
                 ``[-l [LED_CHANNEL [LED_CHANNEL ...]]]``
                 ``[-b BUTTON_CHANNEL] [-t TOTAL_TIME_BLINKING]``
                 ``[--on TIME_ON] [--off TIME_OFF]``

Run the script on the RPi::

    $ run_examples

Run the code for example #1 on your computer using `SimulRPi.GPIO`_ which
simulates `RPi.GPIO`_::

    $ run_examples -s -e 1

.. _installed: https://github.com/raul23/SimulRPi#readme
.. _RPi.GPIO:
    https://pypi.org/project/RPi.GPIO/
.. _SimulRPi: https://github.com/raul23/SimulRPi
.. _SimulRPi.GPIO: https://github.com/raul23/SimulRPi

"""
# TODO: add URL for installed that points to installation section
import argparse
import time
from SimulRPi import __version__
from SimulRPi.mapping import default_channel_to_key_map as channel_key_map
from SimulRPi.utils import blink_led


GPIO = None
DEFAULT_BUTTON_CHANNEL = 20
DEFAULT_KEY_NAME = channel_key_map[DEFAULT_BUTTON_CHANNEL]
DEFAULT_LED_CHANNELS = [10, 11, 12]
DEFAULT_TOTAL_TIME_BLINKING = 4
DEFAULT_TIME_ON = 0.5
DEFAULT_TIME_OFF = 0.5


def ex1_display_led(channel, time_on=2):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.OUT)
    GPIO.output(channel, GPIO.HIGH)
    time.sleep(time_on)
    GPIO.cleanup()
    return 0


def ex2_display_three_leds(channels, time_on):
    GPIO.setmode(GPIO.BCM)
    for ch in channels:
        GPIO.setup(ch, GPIO.OUT)
        GPIO.output(ch, GPIO.HIGH)
    time.sleep(time_on)
    GPIO.cleanup()
    return 0


def ex3_detect_key(channel):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    key_name = channel_key_map[channel]
    print("Press the key '{}' to exit".format(key_name))
    while True:
        if not GPIO.input(channel):
            print("The key '{}' was pressed".format(key_name))
            break
    GPIO.cleanup()
    return 0


def ex4_blink_led(channel, total_time_blinking=4, time_on=0.5, time_off=0.5):
    """Blink a LED for 4 seconds.

    The led is turned on for `time_between_on` seconds, and

    Press :obj:`ctrl` + :obj:`c` to stop the blinking and exit from the
    function.

    Parameters
    ----------
    channel : int
        GPIO channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).
    total_time_blinking : float, optional
        Total time in seconds the LED will be blinking. The default value is 4
        seconds.
    time_on : float, optional
        Time in seconds the LED will stay turned ON. The default value is 0.4
        seconds.
    time_off : float, optional
        Time in seconds the LED will stay turned OFF. The default value is 0.4
        seconds.

    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.OUT)
    start = time.time()
    while (time.time() - start) < total_time_blinking:
        try:
            blink_led(channel, time_on, time_off)
        except KeyboardInterrupt:
            break
    GPIO.cleanup()
    return 0


def ex5_blink_led_if_key(led_channel, key_channel, total_time_blinking=10,
                         time_on=1, time_off=0.5):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led_channel, GPIO.OUT)
    GPIO.setup(key_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    key_name = channel_key_map[key_channel]
    print("Press key '{}' to blink a LED".format(key_name))
    while True:
        try:
            if not GPIO.input(key_channel):
                print("Key '{}' pressed".format(key_name))
                start = time.time()
                while (time.time() - start) < total_time_blinking:
                    blink_led(led_channel, time_on, time_off)
                break
        except KeyboardInterrupt:
            break
    GPIO.cleanup()
    return 0


def setup_argparser():
    """Setup the argument parser for the command-line script.

    The script allows you to run a code examples on your RPi or on your
    computer in which case it will make use of the mock library `SimulRPi`_.

    Returns
    -------
    args :

    """
    # Setup the parser
    parser = argparse.ArgumentParser(
        # usage="%(prog)s [OPTIONS]",
        # prog=os.path.basename(__file__),
        description='''\
Run a code example on your RPi or on your computer in which case it will make 
use of the mock library SimulRPi.''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # ===============
    # General options
    # ===============
    parser.add_argument("-v", "--version", action='version',
                        version='%(prog)s {}'.format(__version__))
    parser.add_argument(
        "-e", type=int, dest="example_number", required=True,
        help='''The number of the code example you want to run. It is 
        required.''')
    parser.add_argument("-s", "--simulation", action="store_true",
                        help="Enable simulation mode, i.e. SimulRPi.GPIO wil "
                             "be used for simulating RPi.GPIO.")
    parser.add_argument(
        "-l", type=int, dest="led_channel", default=DEFAULT_LED_CHANNELS,
        nargs="*",
        help='''The GPIO channels to be used for LEDs. If an example only 
        requires N channels, the first N channels from the provided list will
        be used.''')
    parser.add_argument(
        "-b", type=int, default=DEFAULT_BUTTON_CHANNEL, dest="button_channel",
        help='''The GPIO channel to be used for a push button. The default 
        value is channel 20 which is associated with key `{}`'''.format(
            DEFAULT_KEY_NAME))
    parser.add_argument(
        "-t", type=float, default=DEFAULT_TOTAL_TIME_BLINKING,
        dest="total_time_blinking",
        help='''Total time in seconds LEDs will be blinking.''')
    parser.add_argument(
        "--on", type=float, default=DEFAULT_TIME_ON, dest="time_on",
        help='''Time in seconds the LED will stay turned ON.''')
    parser.add_argument(
        "--off", type=float, default=DEFAULT_TIME_OFF, dest="time_off",
        help='''Time in seconds the LED will stay turned OFF.''')
    return parser.parse_args()


def main():
    global GPIO
    args = setup_argparser()
    if args.simulation:
        import SimulRPi.GPIO as GPIO
        print("Simulation mode enabled")
    else:
        import RPi.GPIO as GPIO
    import SimulRPi.utils as utils
    utils.GPIO = GPIO
    # =======
    # Actions
    # =======
    retcode = 1
    try:
        if args.example_number == 1:
            retcode = ex1_display_led(args.led_channel[0], args.time_on)
        elif args.example_number == 2:
            retcode = ex2_display_three_leds(args.led_channel, args.time_on)
        elif args.example_number == 3:
            retcode = ex3_detect_key(args.button_channel)
        elif args.example_number == 4:
            retcode = ex4_blink_led(args.led_channel[0],
                                    args.total_time_blinking,
                                    args.time_on,
                                    args.time_off)
        elif args.example_number == 5:
            retcode = ex5_blink_led_if_key(args.led_channel[0],
                                           args.button_channel,
                                           args.total_time_blinking,
                                           args.time_on,
                                           args.time_off)
        else:
            print("Example # {} not found".format(args.example_number))
    except Exception as e:
        print(e)
    finally:
        return retcode


if __name__ == '__main__':
    retcode = main()
    # print("Program exited with {}".format(retcode))
