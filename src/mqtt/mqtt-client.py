import paho.mqtt.client as mqtt
import time

id_name = "client1"
broker_addr = "192.168.0.17"
topic = "home/test/bulb"

# Settings
client = mqtt.Client(id_name)
client.connect(broker_addr)

# Start Client.
client.loop_start()
client.subscribe(topic)
time.sleep(9)
client.loop_stop()
client.disconnect()


# client.on_connect=handle_connected
# client.on_message = handle_msg
# client.on_log=handle_log
# client.loop_forever()
def handle_msg(client, userdata, message):
    print("Received: ", str(message.payload.decode("utf-8", "ignore")))
    print("Topic: ", message.topic)
    print("QOS: ", message.qos)
    print("Retain Flag: ", message.retain)


def handle_log(client, userdata, level, buf):
    print("[LOG] " + buf)


def handle_connected(client, userdata, flags, rc):
    if rc == 0:
        print("[INFO] Connected")
    else:
        print("[ERR] Failed Connection, ", rc)
