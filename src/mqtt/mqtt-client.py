import paho.mqtt.client as mqtt
import time
import ecdh 
import socket
import os
import signals
import serial
import onetimepad
import string
import random
from tqdm import tqdm
import traceback

LAYER = 128
HEIGHT = 7

class Colors:
    INFO = "\033[96m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    END = "\033[0m"

id_name = "sensor1"
broker_addr = "192.168.0.23"
topic = "home/test/random"

def handle_msg(client, userdata, message):
    print("Received: ", str(message.payload.decode("utf-8", "ignore")))
    print("Received: ", str(message.payload))
    print("Topic: ", message.topic)
    print("QOS: ", message.qos)
    print("Retain Flag: ", message.retain)

def handle_log(client, userdata, level, buf):
    print("[LOG] " + buf)

def handle_connected(client, userdata, flags, rc):
    if rc ==0:
        print("[INFO] Connected")
    else:
        print("[ERR] Failed Connection, ", rc)

def dh_handle_handshake(sock: socket.SocketIO) -> bytes:
    ec = ecdh.ECDH(sock)

    # 1. Send A (pub key)
    pub = ec.export_key()
    ec.send_pub_key(pub)

    # 2. Recv B (peer pub key)
    peer_pub = ec.recv_pub_key()

    # 3. Generate Shared Key
    peer_pub_key = ec.import_key(peer_pub)
    share_key = ec.shared_key(peer_pub_key)
    return share_key

try:
    addr = broker_addr
    port = 1883
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((addr, port))
    share_key = dh_handle_handshake(sock)
    print(f"{Colors.INFO}[INFO]{Colors.END} ECDH Key = ", share_key)

    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )

    # 2 Layers with height of 7.
    print(f"{Colors.INFO}[INFO]{Colors.END} Reading OTP.")
    otp_tree = signals.recv_otp(ser, LAYER, HEIGHT)
    print(f"{Colors.INFO}[INFO]{Colors.END} Done Reading OTP.")

    print(f"{Colors.INFO}[INFO]{Colors.END} Sending OTP.")
    # Sending the OTP to proxy.
    for tree in tqdm(otp_tree):
        data = f"{tree}"
        byte_data = onetimepad.encrypt(data, share_key.hex())
        length = f"{len(byte_data)}"
        # 1. Send the total byte size.
        sock.send(length.encode())
        time.sleep(.3)
        # 2. Send the data.
        size = sock.send(byte_data.encode())
        time.sleep(.3)
    sock.close()
    print(f"{Colors.INFO}[INFO]{Colors.END} Done Sending OTP.")

    try: 
        count = 0
        while True:
            # Fetch the key & layer with generated path.
            path, key = signals.recv_key(ser, HEIGHT)
            layer = signals.recv_layer(ser)
            # print(f"{Colors.INFO}[INFO]{Colors.END} Path: {path} Layer: {layer} Key: {key}")
            if key == 0 :
                break

            time.sleep(.5)
            client = mqtt.Client(client_id=id_name, otp=True, secret=f"{key}", path=path, layer=layer)
            # client.on_message=handle_msg
            # client.on_log=handle_log

            client.connect(broker_addr)
            client.loop_start()

            letters = string.ascii_letters
            limit = random.randrange(1, 20)
            data = ''.join(random.choice(letters) for i in range(limit)) 
            client.publish(topic, f"{data}")
            count += 1
            print(
                    f"{Colors.INFO}[INFO]{Colors.END} Session {count} => Path: {path} Key: {key} Layer: {layer} Data: {data} Len: {len(data)}"
            )
            time.sleep(.5)

            client.loop_stop()
            client.disconnect()

    except Exception as e:
        print(f"{Colors.ERROR}[ERROR]{Colors.END} Connect problem ", traceback.format_exc())
        os.sys.exit(0)

except KeyboardInterrupt:
    os.sys.exit(0)

except Exception as e:
    print(f"{Colors.ERROR}[ERROR]{Colors.END} Program Problem ", traceback.format_exc())
    os.sys.exit(0)
