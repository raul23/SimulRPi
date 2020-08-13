import logging
import os
import time
import unittest
from logging import NullHandler

from SimulRPi import GPIO, utils
from pyutils.genutils import get_qualname
from pyutils.testutils import TestBase

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())


class TestUtils(TestBase):
    TEST_MODULE_QUALNAME = get_qualname(utils)
    LOGGER_NAME = __name__
    SHOW_FIRST_CHARS_IN_LOG = 0
    CREATE_SANDBOX_TMP_DIR = False
    CREATE_DATA_TMP_DIR = False

    # @unittest.skip("test_blink_led()")
    def test_blink_led(self):
        enable_printing = False
        channel = 1
        mode = GPIO.BCM
        time_led_on = 1
        time_led_off = 1
        delta = 0.5
        self.log_test_method_name()
        extra_msg = "Case where a LED (ch={}) is checked that is <color>" \
                    "blinking correctly</color>".format(channel)
        self.log_main_message(extra_msg=extra_msg)
        GPIO.setprinting(enable_printing)
        GPIO.setmode(mode)
        GPIO.setup(channel, GPIO.OUT)
        start = time.time()
        utils.blink_led(channel, time_led_on, time_led_off)
        end = time.time()
        duration = end - start
        msg = "The blinking LED is taking too long with {} seconds. It " \
              "should take at most {} seconds".format(
                duration,
                time_led_on + time_led_off + delta)
        self.assertAlmostEqual(duration, time_led_on + time_led_off,
                               delta=delta, msg=msg)
        pin = GPIO.manager.pin_db.get_pin_from_channel(channel)
        msg = "The pin on channel {} shouldn't be None".format(channel)
        self.assertIsNotNone(pin, msg)
        msg = "At the end of the blinking, the LED should be at state {} " \
              "but it ended with {}".format(GPIO.LOW, GPIO.HIGH)
        self.assertFalse(pin.state, msg)
        GPIO.cleanup()
        # Test cleanup(): manager's attributes should be correctly set
        msg = "The GPIO.manager's mode should be None"
        self.assertIsNone(GPIO.manager.mode, msg)
        msg = "The displaying thread should not be alive"
        self.assertFalse(GPIO.manager.th_display_leds.is_alive(), msg)
        # TODO: listener thread is not created on travis (no pynput)
        msg = "The listener thread should not be created because testing on " \
              "travis"
        self.assertIsNone(GPIO.manager.th_listener, msg)
        logger.info(
            "<color>RESULT:</color> The LED blinked for {} seconds <color>as "
            "expected</color> without errors".format(duration))
