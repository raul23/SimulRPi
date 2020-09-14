import sys
import time

if len(sys.argv) > 1 and sys.argv[1] == '-s':
    import SimulRPi.GPIO as GPIO

    msg1 = "\nPress key 'cmd_r' to blink a LED"
    msg2 = "Key 'cmd_r' pressed!"
else:
    import RPi.GPIO as GPIO

    msg1 = "\nPress button to blink a LED"
    msg2 = "Button pressed!"

led_channel = 10
button_channel = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_channel, GPIO.OUT)
GPIO.setup(button_channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print(msg1)
while True:
    try:
        if not GPIO.input(button_channel):
            print(msg2)
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
