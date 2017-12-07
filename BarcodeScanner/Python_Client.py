import websocket
import RPi.GPIO as GPIO
import time

LED = 38

GPIO.setmode(GPIO.BOARD)
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
    entry = GPIO.input(LED)
    while True:
        print("Jetzt Scannen")
        x = input()
        if entry:
            message = '{"user":"%s","entry":true,"time":%d}' % (x, time.time())
            print("button true")
            print(message)
            ws.send(message)
        else:
            message = '{"user":"%s","entry":false,"time":%d}' % (x, time.time())
            print("button false")
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