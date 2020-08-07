#!/usr/script/env python
"""Script for executing code examples on a Raspberry Pi or computer (
simulation).

This script allows you to run different code examples on your Raspberry Pi (RPi)
or computer in which case it will make use of the mock library `SimulRPi`_ wich
partly fakes `RPi.GPIO`_.

The code examples test different parts of the mock library `SimulRPi`_ in order
to show what it is capable of simulating from an RPi:

    * Turn on/off LEDs
    * Detect pressed button and perform an action

Usage
-----

.. highlight:: console

Once the **SimulRPi** package is `installed`_, you should have access to
the :mod:`run_examples` script::

    run_examples [-h] [-v] -e EXAMPLE_NUMBER [-s]
                 [-l [LED_CHANNEL [LED_CHANNEL ...]]]
                 [-b BUTTON_CHANNEL] [-t TOTAL_TIME_BLINKING]
                 [--on TIME_ON] [--off TIME_OFF]

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
from SimulRPi.mapping import default_channel_to_key_map
from SimulRPi.utils import blink_led, turn_on_led


GPIO = None
SIMULATION = False
DEFAULT_BUTTON_CHANNEL = 20
DEFAULT_KEY_NAME = default_channel_to_key_map[DEFAULT_BUTTON_CHANNEL]
DEFAULT_LED_CHANNELS = [10, 11, 12]
DEFAULT_TOTAL_TIME_BLINKING = 4
DEFAULT_TIME_ON = 1
DEFAULT_TIME_OFF = 1


def _show_msg(msg, channel):
    if SIMULATION:
        key_name = GPIO.manager.channel_to_key_map[channel]
        msg = msg.format("key '{}'".format(key_name))
    else:
        msg = msg.format("button")
    print("\n" + msg)


def _show_msg_pressed_button(channel):
    _show_msg("The {} was pressed", channel)


def _show_msg_to_turn_on(channel):
    _show_msg("Press the {} to turn on light", channel)


def ex1_turn_on_led(channel, time_on=3):
    """**Example 1:** Turn ON a LED for some specified time.

    A LED will be turned on for ``time_on`` seconds.

    Parameters
    ----------
    channel : int
        Output GPIO channel number based on the numbering system you have
        specified (`BOARD` or `BCM`).
    time_on : float, optional
        Time in seconds the LED will stay turned ON. The default value is 3
        seconds.

    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.OUT)
    turn_on_led(channel)
    time.sleep(time_on)
    GPIO.cleanup()


def ex2_turn_on_many_leds(channels, time_on=3):
    """**Example 2:** Turn ON multiple LEDs for some specified time.

    All LEDs will be turned on for ``time_on`` seconds.

    Parameters
    ----------
    channels : list
        List of output GPIO channel numbers based on the numbering system you
        have specified (`BOARD` or `BCM`).
    time_on : float, optional
        Time in seconds the LEDs will stay turned ON at a time. The default
        value is 3 seconds.

    """
    GPIO.setmode(GPIO.BCM)
    for ch in channels:
        GPIO.setup(ch, GPIO.OUT)
        turn_on_led(ch)
    time.sleep(time_on)
    GPIO.cleanup()


def ex3_detect_button(channel):
    """**Example 3:** Detect if a button is pressed.

    The function waits for the specified button to be pressed associated with
    the given ``channel``. As soon as the button is pressed, a message is
    printed and the function exits.

    Parameters
    ----------
    channel : int
        Input GPIO channel number based on the numbering system you have
        specified (`BOARD` or `BCM`).

    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    _show_msg_to_turn_on(channel)
    while True:
        if not GPIO.input(channel):
            _show_msg_pressed_button(channel)
            break
    GPIO.cleanup()


def ex4_blink_led(channel, total_time_blinking=4, time_on=0.5, time_off=0.5):
    """**Example 4:** Blink a LED for some specified time.

    The led will blink for a total of ``total_time_blinking`` seconds. The LED
    will stay turned on for ``time_on`` seconds before turning off for
    ``time_off`` seconds, and so on until ``total_time_blinking`` seconds
    elapse.

    Press :obj:`ctrl` + :obj:`c` to stop the blinking completely and exit from
    the function.

    Parameters
    ----------
    channel : int
        Output GPIO channel number based on the numbering system you have
        specified (`BOARD` or `BCM`).
    total_time_blinking : float, optional
        Total time in seconds the LED will be blinking. The default value is 4
        seconds.
    time_on : float, optional
        Time in seconds the LED will stay turned ON at a time. The default
        value is 0.5 seconds.
    time_off : float, optional
        Time in seconds the LED will stay turned OFF at a tme. The default
        value is 0.5 seconds.

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


def ex5_blink_led_if_button(led_channel, button_channel, total_time_blinking=10,
                            time_on=1, time_off=0.5):
    """**Example 5:** If a button is pressed, blink a LED for some specified
    time.

    As soon as the specified button from the given ``button_channel`` is
    pressed, the LED will blink for a total of ``total_time_blinking`` seconds.

    The LED will stay turned on for ``time_on`` seconds before turning off for
    ``time_off`` seconds, and so on until ``total_time_blinking`` seconds
    elapse.

    Press :obj:`ctrl` + :obj:`c` to stop the blinking completely and exit from
    the function.

    Parameters
    ----------
    led_channel : int
        Output GPIO channel number based on the numbering system you have
        specified (`BOARD` or `BCM`).
    button_channel : int
        Input GPIO channel number based on the numbering system you have
        specified (`BOARD` or `BCM`).
    total_time_blinking : float, optional
        Total time in seconds the LED will be blinking. The default value is 4
        seconds.
    time_on : float, optional
        Time in seconds the LED will stay turned ON at a time. The default
        value is 0.5 seconds.
    time_off : float, optional
        Time in seconds the LED will stay turned OFF at a tme. The default
        value is 0.5 seconds.

    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led_channel, GPIO.OUT)
    GPIO.setup(button_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    _show_msg_to_turn_on(button_channel)
    while True:
        try:
            if not GPIO.input(button_channel):
                _show_msg_pressed_button(button_channel)
                start = time.time()
                while (time.time() - start) < total_time_blinking:
                    blink_led(led_channel, time_on, time_off)
                break
        except KeyboardInterrupt:
            break
    GPIO.cleanup()


def setup_argparser():
    """Setup the argument parser for the command-line script.

    The script allows you to run a code examples on your RPi or on your
    computer in which case it will make use of the module `SimulRPi.GPIO`_
    which partly fakes `RPi.GPIO`_.

    Returns
    -------
    args : argparse.Namespace
        Simple class used by default by ``parse_args()`` to create an object
        holding attributes and return it [1]_.

    References
    ----------
    .. [1] `argparse.Namespace
       <https://docs.python.org/3.7/library/argparse.html#argparse.Namespace>`_.

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
        value is channel 20 which is associated with the key `{}`.'''.format(
            DEFAULT_KEY_NAME))
    parser.add_argument(
        "-k", default=DEFAULT_KEY_NAME, dest="key_name",
        help='''The name of the key associated with the button channel. The 
        name must be one of those recognized by the module `pynput`. See the
        SimulRPi documentation for a list of valid key names: 
        https://bit.ly/2Pw1OBe. Example: `alt`, `cmd_r`'''.format(
            DEFAULT_KEY_NAME))
    parser.add_argument(
        "-t", type=float, default=DEFAULT_TOTAL_TIME_BLINKING,
        dest="total_time_blinking",
        help='''Total time in seconds LEDs will be blinking.''')
    parser.add_argument(
        "--on", type=float, default=DEFAULT_TIME_ON, dest="time_on",
        help='''Time in seconds the LED will stay turned ON at a time.''')
    parser.add_argument(
        "--off", type=float, default=DEFAULT_TIME_OFF, dest="time_off",
        help='''Time in seconds the LED will stay turned OFF at a time.''')
    return parser.parse_args()


def main():
    """Main entry-point to the script.

    According to the user's choice of action, the script might run one of the
    specified code examples.

    If the simulation flag (`-s`) is used, then the the module
    `SimulRPi.GPIO`_ will be used which partly fakes `RPi.GPIO`_.

    Notes
    -----
    Only one action at a time can be performed.

    """
    global GPIO, SIMULATION
    args = setup_argparser()
    if args.simulation:
        import SimulRPi.GPIO as GPIO
        SIMULATION = True
        print("Simulation mode enabled")
        if args.key_name != DEFAULT_KEY_NAME:
            key_channel_map = {args.key_name: args.button_channel}
            GPIO.setkeymap(key_channel_map)
    else:
        import RPi.GPIO as GPIO
    import SimulRPi.utils as utils
    utils.GPIO = GPIO
    # =======
    # Actions
    # =======
    retcode = 0
    try:
        if args.example_number == 1:
            ex1_turn_on_led(args.led_channel[0], args.time_on)
        elif args.example_number == 2:
            ex2_turn_on_many_leds(args.led_channel, args.time_on)
        elif args.example_number == 3:
            ex3_detect_button(args.button_channel)
        elif args.example_number == 4:
            ex4_blink_led(args.led_channel[0], args.total_time_blinking,
                          args.time_on, args.time_off)
        elif args.example_number == 5:
            ex5_blink_led_if_button(args.led_channel[0], args.button_channel,
                                    args.total_time_blinking, args.time_on,
                                    args.time_off)
        else:
            print("Example # {} not found".format(args.example_number))
    except Exception as e:
        print(e)
        retcode = 1
    finally:
        return retcode


if __name__ == '__main__':
    retcode = main()
    # print("Program exited with {}".format(retcode))
