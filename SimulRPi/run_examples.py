#!/usr/bin/env python
"""Script for executing code examples on a Raspberry Pi or computer (simulation).

This script allows you to run different code examples on your Raspberry Pi (RPi)
or computer in which case it will make use of the `SimulRPi`_ library which
partly fakes `RPi.GPIO`_.

The code examples test different parts of the ``SimulRPi`` library in order to
show what it is capable of simulating from I/O devices connected to an RPi:

    * Turn on/off LEDs: blink LED symbols in the terminal
    * Detect pressed button: monitor keyboard with `pynput`_

Usage
-----

.. highlight:: console

Once the **SimulRPi** package is `installed`_, you should have access to
the :mod:`~SimulRPi.run_examples` script::

    $ run_examples -h

    run_examples [-h] [-v] -e EXAMPLE_NUMBER [-m {BOARD,BCM}] [-s]
                 [-l [LED_CHANNEL [LED_CHANNEL ...]]]
                 [-b BUTTON_CHANNEL] [-k KEY_NAME]
                 [-t TOTAL_TIME_BLINKING] [--on TIME_LED_ON]
                 [--off TIME_LED_OFF] [-a]

Run the code for example 1 on the **RPi** with default values for the options
``-l`` (channel 10) and ``--on`` (1 second)::

    $ run_examples -e 1

Run the code for example 1 on your **computer** using the simulation module
:mod:`SimulRPi.GPIO`::

    $ run_examples -s -e 1

.. TODO: find if we can load the list of options from a separate file

"""
# TODO: add printing or logging
import argparse
import time
import traceback

from SimulRPi import __version__
from SimulRPi.mapping import default_channel_to_key_map
from SimulRPi.utils import blink_led, turn_off_led, turn_on_led

GPIO = None
SIMULATION = False
# TODO: necessary? maybe in a separate file
DEFAULT_BUTTON_CHANNEL = 17
DEFAULT_KEY_NAME = default_channel_to_key_map[DEFAULT_BUTTON_CHANNEL]
DEFAULT_LED_CHANNELS = [9, 10, 11]
DEFAULT_TOTAL_TIME_BLINKING = 4
DEFAULT_TIME_LEDS_ON = 1
DEFAULT_TIME_LEDS_OFF = 1


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
        Output channel number based on the numbering system you have
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


def ex2_turn_on_many_leds(channels, time_leds_on=3):
    """**Example 2:** Turn ON multiple LEDs for some specified time.

    All LEDs will be turned on for ``time_leds_on`` seconds.

    Parameters
    ----------
    channels : list
        List of output channel numbers based on the numbering system you have
        specified (`BOARD` or `BCM`).
    time_leds_on : float, optional
        Time in seconds the LEDs will stay turned ON. The default value is 3
        seconds.

    """
    msg = "Ex 2: turn ON {nb_leds} LED{plural1} for a total of {time} " \
          "second{plural2}\n".format(
            nb_leds=len(channels),
            plural1="s" if len(channels) > 1 else "",
            time=time_leds_on,
            plural2="s" if time_leds_on >= 2 else "")
    print(msg)
    GPIO.setup(channels, GPIO.OUT)
    turn_on_led(channels)
    time.sleep(time_leds_on)


def ex3_detect_button(channel):
    """**Example 3:** Detect if a button is pressed.

    The function waits for the button to be pressed associated with the given
    ``channel``. As soon as the button is pressed, a message is printed and the
    function exits.

    Parameters
    ----------
    channel : int
        Input channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).


    .. note::

        If the simulation mode is enabled (``-s``), the specified keyboard key
        will be detected if pressed. The keyboard key can be specified through
        the command line option ``-b`` (button channel) or ``-k`` (the key
        name, e.g. '*ctrl*'). See `script's usage`_.

    """
    msg = "Ex 3: detect if the {key_or_button} [{channel}] is pressed\n".format(
        key_or_button="{}", channel=channel)
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
        Output channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).
    total_time_blinking : float, optional
        Total time in seconds the LED will be blinking. The default value is 4
        seconds.
    time_led_on : float, optional
        Time in seconds the LED will stay turned ON at a time. The default
        value is 0.5 second.
    time_led_off : float, optional
        Time in seconds the LED will stay turned OFF at a time. The default
        value is 0.5 second.

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
        Output channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).
    button_channel : int
        Input channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).
    total_time_blinking : float, optional
        Total time in seconds the LED will be blinking. The default value is 4
        seconds.
    time_led_on : float, optional
        Time in seconds the LED will stay turned ON at a time. The default
        value is 0.5 second.
    time_led_off : float, optional
        Time in seconds the LED will stay turned OFF at a time. The default
        value is 0.5 second.


    .. note::

        If the simulation mode is enabled (``-s``), the specified keyboard key
        will be detected if pressed. The keyboard key can be specified through
        the command line option ``-b`` (button channel) or ``-k`` (the key
        name, e.g. 'ctrl'). See `script's usage`_.

    .. TODO: find if we can avoid duplicates of notes and other notices

    """
    msg = "Ex 5: if the {key_or_button} [{button_channel}] is pressed, blink " \
          "a LED [{led_channel}] for {time} second{plural}\n".format(
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
    computer. In the latter case, it will make use of the
    `SimulRPi.GPIO`_ module which partly fakes `RPi.GPIO`_.

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
Run a code example on your Raspberry Pi (RPi) or computer. In the latter case, 
the script will make use of the SimulRPi library which partly fakes RPi.GPIO 
and also simulates I/O devices connected to an RPi such as LEDs and push buttons 
by blinking small circles on the terminal and listening to pressed keyboard keys.
''',
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
        "-m", "--mode", choices=["BCM", "BOARD"], default="BCM",
        help="Set the numbering system (BCM or BOARD) used to identify the "
             "I/O pins on an RPi. ")
    parser.add_argument("-s", "--simulation", action="store_true",
                        help="Enable simulation mode, i.e. SimulRPi.GPIO will "
                             "be used for simulating RPi.GPIO.")
    parser.add_argument(
        "-l", type=int, dest="led_channels", default=DEFAULT_LED_CHANNELS,
        nargs="*",
        help='''The channel numbers to be used for LEDs. If an example only 
        requires 1 channel, the first channel from the provided list will be 
        used.''')
    parser.add_argument(
        "-b", type=int, default=DEFAULT_BUTTON_CHANNEL, dest="button_channel",
        help='''The channel number to be used for a push button. The default 
        value is channel {} which is associated by default with the key 
        `{}`.'''.format(DEFAULT_BUTTON_CHANNEL, DEFAULT_KEY_NAME))
    parser.add_argument(
        "-k", default=DEFAULT_KEY_NAME, dest="key_name",
        help='''The name of the keyboard key associated with the button 
        channel. The name must be one of those recognized by the `pynput` 
        package. See the SimulRPi documentation for a list of valid key names: 
        https://bit.ly/2Pw1OBe. Example: `alt`, `ctrl_r`'''.format(
            DEFAULT_KEY_NAME))
    parser.add_argument(
        "-t", type=float, default=DEFAULT_TOTAL_TIME_BLINKING,
        dest="total_time_blinking",
        help='''Total time in seconds LEDs will be blinking.''')
    parser.add_argument(
        "--on", type=float, default=DEFAULT_TIME_LEDS_ON, dest="time_leds_on",
        help='''Time in seconds the LEDs will stay turned ON at a time.''')
    parser.add_argument(
        "--off", type=float, default=DEFAULT_TIME_LEDS_OFF, dest="time_leds_off",
        help='''Time in seconds the LEDs will stay turned OFF at a time.''')
    parser.add_argument(
        "-a", "--ascii", dest="ascii", action="store_true",
        help='''Use ASCII-based LED symbols. Useful if you are having problems 
        displaying the default LED signs that make use of special characters.
        However, it is recommended to fix your display problems which might be
        caused by locale settings not set correctly. Check the article 
        'Display problems' @ https://bit.ly/35B8bfs for more info about 
        solutions to display problems.''')
    return parser.parse_args()


def main():
    """Main entry-point to the script.

    According to the user's choice of action, the script might run one of the
    specified code examples.

    If the simulation flag (`-s`) is used, then the `SimulRPi.GPIO`_ module
    will be used which partly fakes `RPi.GPIO`_.

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
        if args.ascii:
            GPIO.setdefaultsymbols("default_ascii")
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
    led_channels = []
    try:
        if args.example_number == 1:
            ex1_turn_on_led(args.led_channels[0], args.time_leds_on)
            led_channels.append(args.led_channels[0])
        elif args.example_number == 2:
            ex2_turn_on_many_leds(args.led_channels, args.time_leds_on)
            led_channels.append(args.led_channels)
        elif args.example_number == 3:
            ex3_detect_button(args.button_channel)
        elif args.example_number == 4:
            ex4_blink_led(args.led_channels[0], args.total_time_blinking,
                          args.time_leds_on, args.time_leds_off)
        elif args.example_number == 5:
            ex5_blink_led_if_button(args.led_channels[0], args.button_channel,
                                    args.total_time_blinking,
                                    args.time_leds_on,
                                    args.time_leds_off)
        else:
            print("Example # {} not found".format(args.example_number))
        if SIMULATION:
            GPIO.wait(0.5)
    except Exception:
        retcode = 1
        traceback.print_exc()
    except KeyboardInterrupt:
        # ctrl + c
        pass
    finally:
        if SIMULATION:
            GPIO.setprinting(False)
        # Turn off all LEDs
        for ch in led_channels:
            turn_off_led(ch)
        # Cleanup will be performed after each code example's function exits
        # or when there is an exception (including ctrl+c = KeyboardInterrupt)
        GPIO.cleanup()
        return retcode


if __name__ == '__main__':
    retcode = main()
    print("\n\nProgram exited with {}".format(retcode))
