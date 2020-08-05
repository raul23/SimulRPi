import SimulRPi.GPIO as GPIO


def display_three_leds(channels):
    GPIO.setmode(GPIO.BCM)
    for ch in channels:
        GPIO.setup(ch, GPIO.OUT)
        GPIO.output(ch, GPIO.HIGH)
    GPIO.cleanup()


if __name__ == '__main__':
    display_three_leds([10, 11, 12])
