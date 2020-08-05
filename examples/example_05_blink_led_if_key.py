"""

"""
import time
import SimulRPi.GPIO as GPIO
from SimulRPi.mapping import default_key_to_channel_map as default_map


def blink_led_if_pressed_key(led_channel, key_channel):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led_channel, GPIO.OUT)
    GPIO.setup(key_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    reverse_default = {v: k for k, v in default_map.items()}
    key_name = reverse_default[key_channel]
    print("Press key '{}' to blink a LED".format(key_name))
    while True:
        try:
            if not GPIO.input(key_channel):
                print("Key '{}' pressed".format(key_name))
                start = time.time()
                while (time.time() - start) < 3:
                    GPIO.output(led_channel, GPIO.HIGH)
                    time.sleep(0.5)
                    GPIO.output(led_channel, GPIO.LOW)
                    time.sleep(0.5)
                break
        except KeyboardInterrupt:
            break
    GPIO.cleanup()


if __name__ == '__main__':
    blink_led_if_pressed_key(10, 20)
