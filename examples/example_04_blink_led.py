import time
import SimulRPi.GPIO as GPIO


def display_led(channel):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.OUT)
    start = time.time()
    while (time.time() - start) < 5:
        try:
            GPIO.output(channel, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(channel, GPIO.LOW)
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
    GPIO.cleanup()


if __name__ == '__main__':
    display_led(101)
