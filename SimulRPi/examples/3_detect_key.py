import SimulRPi.GPIO as GPIO
from SimulRPi.mapping import default_key_to_channel_map as default_map


def detect_key(channel):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    reverse_default = {v: k for k, v in default_map.items()}
    key_name = reverse_default[channel]
    print("Press key '{}' to exit".format(key_name))
    while True:
        if not GPIO.input(channel):
            print("Key '{}' pressed".format(key_name))
            break
    GPIO.cleanup()


if __name__ == '__main__':
    detect_key(17)
