import paho.mqtt.client as mqtt
import time

id_name = "sensor1"
broker_addr = "192.168.0.11"
topic = "home/test/bulb"

# Settings
client = mqtt.Client(id_name)
client.connect(broker_addr)

# Start Publisher.
client.loop_start()
client.publish(topic, "ON")
time.sleep(8)
client.loop_stop()
client.disconnect()

# client.loop_forever()
