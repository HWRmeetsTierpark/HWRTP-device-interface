import time
import websocket

import RPi.GPIO as GPIO

LED = 36

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(LED, GPIO.IN)


def on_message(message):
    """
    client received message
    :param message: Message
    """
    print("message:")
    print(message)


def on_error(error):
    """
    error while websocket-connection
    :param error: Error
    """
    print("error:")
    print(error)


def on_close():
    """
    websocket-connection closed
    :return:
    """
    print("### closed ###")



def on_open(ws):
    """
    connection created
    :param ws: websocket-client
    """
    global LED
    while True:
        print("Jetzt Scannen")
        x = input()  # read input from console
        entry = (GPIO.input(LED) == 1)  # does the check in or out?
        message = '{"user":"%s","entry":%s,"time":%d}' % (x, str(entry).lower(), time.time())  # create message
        print(message)
        ws.send(message)  # send message


""" start """
if __name__ == "__main__":
    # get time
    print(str(time.time()))

    # connect to websocket at localhost port 8080
    ws = websocket.WebSocketApp("ws://localhost:9000",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
