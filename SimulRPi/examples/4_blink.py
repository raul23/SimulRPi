"""Example 4: blink a LED for 4 seconds

Blink a LED on channel 20 for 4 seconds (or until you press :obj:`ctrl` +
:obj:`c`)

"""
import time
import SimulRPi.GPIO as GPIO


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
    blink_led(20)
