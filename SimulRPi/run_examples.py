#!/usr/script/env python
"""Script for executing code examples on a Raspberry Pi or computer (simulation).

This script allows you to run different code examples on your Raspberry Pi (RPi)
or computer in which case it will make use of the mock library `SimulRPi`_
which partly fakes `RPi.GPIO`_.

..
   TODO: change URLs for 'SimulRPi.GPIO' to point to the real one

The code examples test different parts of the mock library ``SimulRPi`` in
order to show what it is capable of simulating from an RPi:

    * Turn on/off LEDs
    * Detect pressed button and perform an action

Usage
-----

.. highlight:: console

Once the **SimulRPi** package is `installed`_, you should have access to
the :mod:`run_examples` script::

    $ run_examples -h

    run_examples [-h] [-v] -e EXAMPLE_NUMBER [-m {BOARD,BCM}] [-s]
                 [-l [LED_CHANNEL [LED_CHANNEL ...]]]
                 [-b BUTTON_CHANNEL] [-k KEY_NAME]
                 [-t TOTAL_TIME_BLINKING] [--on TIME_LED_ON]
                 [--off TIME_LED_OFF]

Run the script on the RPi::

    $ run_examples

Run the code for example **#1** on your computer using `SimulRPi.GPIO`_ which
simulates `RPi.GPIO`_: and default values for the options `-l` (channel 10) and
-`-on` (1 second)::

    $ run_examples -s -e 1

.. _installed:
    https://simulrpi.readthedocs.io/en/latest/README_docs.html#installation-instructions
.. _RPi.GPIO:
    https://pypi.org/project/RPi.GPIO/
.. _SimulRPi: https://test.pypi.org/project/SimulRPi/
.. _SimulRPi.GPIO: https://test.pypi.org/project/SimulRPi/
.. _script's usage: #usage

..
    TODO: add URL for installed that points to installation section
    TODO: find if we can load the list of options from a separate file
    TODO: place default values in separate file

"""
import argparse
import time
import traceback

from SimulRPi import __version__
from SimulRPi.mapping import default_channel_to_key_map
from SimulRPi.utils import blink_led, turn_on_led


GPIO = None
SIMULATION = False
DEFAULT_BUTTON_CHANNEL = 13
DEFAULT_KEY_NAME = default_channel_to_key_map[DEFAULT_BUTTON_CHANNEL]
DEFAULT_LED_CHANNELS = [10, 11, 12]
DEFAULT_TOTAL_TIME_BLINKING = 4
DEFAULT_TIME_LED_ON = 1
DEFAULT_TIME_LED_OFF = 1


def _show_msg(msg, channel=None):
    if SIMULATION:
        if channel:
            key_name = GPIO.manager.channel_to_key_map[channel]
            msg = msg.format("key '{}'".format(key_name))
    else:
        msg = msg.format("button")
    print(msg)


def _show_msg_pressed_button(channel):
    _show_msg("\nThe {} was pressed!", channel)


def _show_msg_to_press_key(channel):
    _show_msg("\nPress the {} to exit...", channel)


def _show_msg_to_turn_on(channel):
    _show_msg("\nPress the {} to turn on light ...", channel)


def ex1_turn_on_led(channel, time_led_on=3):
    """**Example 1:** Turn ON a LED for some specified time.

    A LED will be turned on for ``time_led_on`` seconds.

    Parameters
    ----------
    channel : int
        Output GPIO channel number based on the numbering system you have
        specified (`BOARD` or `BCM`).
    time_led_on : float, optional
        Time in seconds the LED will stay turned ON. The default value is 3
        seconds.

    """
    print("Ex 1: turn ON a LED for {time} second{plural}\n".format(
            channel=channel,
            time=time_led_on,
            plural="s" if time_led_on >= 2 else ""
    ))
    GPIO.setup(channel, GPIO.OUT)
    turn_on_led(channel)
    time.sleep(time_led_on)


def ex2_turn_on_many_leds(channels, time_led_on=3):
    """**Example 2:** Turn ON multiple LEDs for some specified time.

    All LEDs will be turned on for ``time_led_on`` seconds.

    Parameters
    ----------
    channels : list
        List of output GPIO channel numbers based on the numbering system you
        have specified (`BOARD` or `BCM`).
    time_led_on : float, optional
        Time in seconds the LEDs will stay turned ON. The default value is 3
        seconds.

    """
    msg = "Ex 2: turn ON {nb_leds} LED{plural1} for a total of {time} " \
          "second{plural2}\n".format(
            nb_leds=len(channels),
            plural1="s" if len(channels) > 1 else "",
            time=time_led_on,
            plural2="s" if time_led_on >= 2 else ""
    )
    print(msg)
    for ch in channels:
        GPIO.setup(ch, GPIO.OUT)
        turn_on_led(ch)
    time.sleep(time_led_on)


def ex3_detect_button(channel):
    """**Example 3:** Detect if a button is pressed.

    The function waits for the button to be pressed associated with the given
    ``channel``. As soon as the button is pressed, a message is printed and the
    function exits.

    Parameters
    ----------
    channel : int
        Input GPIO channel number based on the numbering system you have
        specified (`BOARD` or `BCM`).


    .. note::

        If the simulation mode is enabled (`-s`), the specified keyboard key
        will be detected if pressed. The keyboard key can be specified through
        the command line options `-b` (button channel) or `-k` (the key name,
        e.g. 'ctrl'). See `script's usage`_.

    """
    msg = "Ex 3: detect if the {key_or_button} [{channel}] is pressed\n".format(
        key_or_button={}, channel=channel)
    _show_msg(msg, channel)
    GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    _show_msg_to_press_key(channel)
    while True:
        if not GPIO.input(channel):
            _show_msg_pressed_button(channel)
            break


def ex4_blink_led(channel, total_time_blinking=4, time_led_on=0.5, time_led_off=0.5):
    """**Example 4:** Blink a LED for some specified time.

    The led will blink for a total of ``total_time_blinking`` seconds. The LED
    will stay turned on for ``time_led_on`` seconds before turning off for
    ``time_led_off`` seconds, and so on until ``total_time_blinking`` seconds
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
    time_led_on : float, optional
        Time in seconds the LED will stay turned ON at a time. The default
        value is 0.5 seconds.
    time_led_off : float, optional
        Time in seconds the LED will stay turned OFF at a time. The default
        value is 0.5 seconds.

    """
    msg = "Ex 4: blink a LED for {time} second{plural}\n".format(
            time=total_time_blinking,
            plural="s" if total_time_blinking >= 2 else "")
    print(msg)
    GPIO.setup(channel, GPIO.OUT)
    start = time.time()
    while (time.time() - start) < total_time_blinking:
        try:
            blink_led(channel, time_led_on, time_led_off)
        except KeyboardInterrupt:
            break


def ex5_blink_led_if_button(led_channel, button_channel, total_time_blinking=4,
                            time_led_on=0.5, time_led_off=0.5):
    """**Example 5:** If a button is pressed, blink a LED for some specified
    time.

    As soon as the button from the given ``button_channel`` is pressed, the LED
    will blink for a total of ``total_time_blinking`` seconds.

    The LED will stay turned on for ``time_led_on`` seconds before turning off for
    ``time_led_off`` seconds, and so on until ``total_time_blinking`` seconds
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
    time_led_on : float, optional
        Time in seconds the LED will stay turned ON at a time. The default
        value is 0.5 seconds.
    time_led_off : float, optional
        Time in seconds the LED will stay turned OFF at a time. The default
        value is 0.5 seconds.


    .. note::

        If the simulation mode is enabled (`-s`), the specified keyboard key
        will be detected if pressed. The keyboard key can be specified through
        the command line options `-b` (button channel) or `-k` (the key name,
        e.g. 'ctrl'). See `script's usage`_.

    ..
        TODO: find if we can avoid duplicates of notes and other notices

    """
    msg = "Ex 5: if the {key_or_button} [{button_channel}] is pressed, blink " \
          "a LED [{led_channel}] for {time} second{plural}".format(
            key_or_button="{}",
            button_channel=button_channel,
            led_channel=led_channel,
            time=total_time_blinking,
            plural="s" if total_time_blinking >= 2 else "")
    _show_msg(msg, button_channel)
    GPIO.setup(led_channel, GPIO.OUT)
    GPIO.setup(button_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    _show_msg_to_turn_on(button_channel)
    while True:
        try:
            if not GPIO.input(button_channel):
                _show_msg_pressed_button(button_channel)
                start = time.time()
                while (time.time() - start) < total_time_blinking:
                    blink_led(led_channel, time_led_on, time_led_off)
                break
        except KeyboardInterrupt:
            break


def setup_argparser():
    """Setup the argument parser for the command-line script.

    The script allows you to run a code example on your RPi or on your
    computer. In the latter case, it will make use of the module
    `SimulRPi.GPIO`_ which partly fakes `RPi.GPIO`_.

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
    parser.add_argument(
        "-m", "--mode", choices=["BOARD", "BCM"], default="BCM",
        help="Set the numbering system used to identify the I/O pins on an "
             "RPi. ")
    parser.add_argument("-s", "--simulation", action="store_true",
                        help="Enable simulation mode, i.e. SimulRPi.GPIO wil "
                             "be used for simulating RPi.GPIO.")
    parser.add_argument(
        "-l", type=int, dest="led_channel", default=DEFAULT_LED_CHANNELS,
        nargs="*",
        help='''The GPIO channels to be used for LEDs. If an example only 
        requires 1 channel, the first channel from the provided list will be 
        used.''')
    parser.add_argument(
        "-b", type=int, default=DEFAULT_BUTTON_CHANNEL, dest="button_channel",
        help='''The GPIO channel to be used for a push button. The default 
        value is channel 20 which is associated with the key `{}`.'''.format(
            DEFAULT_KEY_NAME))
    parser.add_argument(
        "-k", default=DEFAULT_KEY_NAME, dest="key_name",
        help='''The name of the keyboard key associated with the button 
        channel. The name must be one of those recognized by the module 
        `pynput`. See the SimulRPi documentation for a list of valid key names: 
        https://bit.ly/2Pw1OBe. Example: `alt`, `cmd_r`'''.format(
            DEFAULT_KEY_NAME))
    parser.add_argument(
        "-t", type=float, default=DEFAULT_TOTAL_TIME_BLINKING,
        dest="total_time_blinking",
        help='''Total time in seconds LEDs will be blinking.''')
    parser.add_argument(
        "--on", type=float, default=DEFAULT_TIME_LED_ON, dest="time_led_on",
        help='''Time in seconds the LED will stay turned ON at a time.''')
    parser.add_argument(
        "--off", type=float, default=DEFAULT_TIME_LED_OFF, dest="time_led_off",
        help='''Time in seconds the LED will stay turned OFF at a time.''')
    return parser.parse_args()


def main():
    """Main entry-point to the script.

    According to the user's choice of action, the script might run one of the
    specified code examples.

    If the simulation flag (`-s`) is used, then the module
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
    # Make sure utils uses the correct GPIO module based on whether we are working
    # with the real GPIO or the fake one (simulation)
    import SimulRPi.utils as utils
    utils.GPIO = GPIO
    # =======
    # Actions
    # =======
    retcode = 0
    # Set the numbering system used to identify the I/O pins on an RPi
    modes = {'BOARD': GPIO.BOARD, 'BCM': GPIO.BCM}
    GPIO.setmode(modes[args.mode.upper()])
    try:
        if args.example_number == 1:
            ex1_turn_on_led(args.led_channel[0], args.time_led_on)
        elif args.example_number == 2:
            ex2_turn_on_many_leds(args.led_channel, args.time_led_on)
        elif args.example_number == 3:
            ex3_detect_button(args.button_channel)
        elif args.example_number == 4:
            ex4_blink_led(args.led_channel[0], args.total_time_blinking,
                          args.time_led_on, args.time_led_off)
        elif args.example_number == 5:
            ex5_blink_led_if_button(args.led_channel[0], args.button_channel,
                                    args.total_time_blinking, args.time_led_on,
                                    args.time_led_off)
        else:
            print("Example # {} not found".format(args.example_number))
    except Exception:
        retcode = 1
        traceback.print_exc()
    except KeyboardInterrupt:
        # ctrl + c
        # print("Exiting...                               ")
        pass
    finally:
        # GPIO.setprinting(False)
        # time.sleep(0.1)
        # print("\nExiting...")
        # print("Cleanup...                               ")
        # Cleanup will be performed after each code example's function exists
        # or when there is an exception (including ctrl+c = KeyboardInterrupt)
        GPIO.cleanup()
        return retcode


if __name__ == '__main__':
    retcode = main()
    print("\nProgram exited with {}".format(retcode))
