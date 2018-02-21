import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

LED = 38
BUTTON = 40
ledOn = False

GPIO.setup(LED, GPIO.OUT)
GPIO.setup(BUTTON, GPIO.IN)


def change_led_state():
    global ledOn
    ledOn = not ledOn
    GPIO.output(LED, ledOn)


if __name__ == "__main__":
    GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=change_led_state)
