import socket
import base64
import os
import websocket
import threading
import time
import re
HOST = "192.168.1.1"
PORT = 80

key = base64.b64encode(os.urandom(16)).decode()

handshake = (
    "GET /websocket HTTP/1.1\r\n"
    "Host: 192.168.1.1\r\n"
    "Upgrade: websocket\r\n"
    "Connection: Upgrade\r\n"
    f"Sec-WebSocket-Key: {key}\r\n"
    "Sec-WebSocket-Version: 13\r\n"
    "Origin: http://192.168.1.1\r\n"
    "\r\n"
)

s = socket.socket()
s.connect((HOST, PORT))

s.send(handshake.encode())




URL = "ws://192.168.1.1/websocket"

def on_message(ws, message):
    # print("RECV:", message.decode('utf-8'))
    msg=message.decode('utf-8')
    msg_arr=msg.split(";")
    for idx, item in  enumerate(msg_arr):
        if item == "U1-19":
            Ta_index= msg_arr[idx + 1 ]
            Ta_temp= msg_arr[idx+2]
            pattern=r"U[0-9]-[0-9]{1,2}"
            if re.match(pattern,msg_arr[idx+2]):
               print ("index:{} Temp{}".format(Ta_index,Ta_temp))
            else:
               print ("index:{}, Temp: {}, Name: {}".format(Ta_index,Ta_temp,msg_arr[idx+3]))
            break
        else:
            continue

def on_error(ws, error):
    print("ERROR:", error)

def on_close(ws, close_status_code, close_msg):
    print("CLOSED")

def on_open(ws):
    print("CONNECTED")

    # optional sender thread
    def run():
        while True:
            ws.send(":REMote:UNITData? UNIT1\r\n")
            print("SEND: hello")
            time.sleep(5)

    threading.Thread(target=run, daemon=True).start()

headers = {
    "Origin": "http://192.168.1.1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}

ws = websocket.WebSocketApp(
    URL,
    header=headers,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()

response = s.recv(4096)
print(response.decode(errors="ignore"))