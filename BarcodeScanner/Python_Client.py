import websocket
import time

def on_message(ws, message):
    print("message:")
    print(message)

def on_error(ws, error):
    print("error:")
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    button = True
    while True:
        print("Jetzt Scannen")
        x = input()
        if button:
            #message = {"user":x, "entry": True, "time":time.time()}
            message = '{"user":"%s","entry":false,"time":%d}' % (x, time.time())
            print("button true")
            print(message)
            ws.send(message)
        else:
            print("Besucher {} betritt den Park".format(x))
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