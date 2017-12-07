import websocket
import RPi.GPIO as GPIO
import time

LED = 36

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(LED, GPIO.IN)

def on_message(ws, message):
    print("message:")
    print(message)

def on_error(ws, error):
    print("error:")
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    global LED
    while True:
        print("Jetzt Scannen")
        x = input()
        entry = (GPIO.input(LED) == 1)
        message = '{"user":"%s","entry":%s,"time":%d}' % (x, str(entry).lower(), time.time())
        print(message)
        ws.send(message)

if __name__ == "__main__":
    #get time
    print(str(time.time()))

    #connect to websocket at localhost port 8080
    ws = websocket.WebSocketApp("ws://localhost:9000",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open

    
    ws.run_forever()