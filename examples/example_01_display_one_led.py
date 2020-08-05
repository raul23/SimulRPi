import SimulRPi.GPIO as GPIO


def display_led(channel):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.OUT)
    GPIO.output(channel, GPIO.HIGH)
    GPIO.cleanup()


if __name__ == '__main__':
    display_led(11)
