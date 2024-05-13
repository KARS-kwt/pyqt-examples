import random
import time
import numpy as np
import json
from paho.mqtt import client as mqtt_client


broker = 'localhost'
port = 1883
topic = "python/mqtt"
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'
# username = 'emqx'
# password = 'public'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client):
    msg_count = 1
    while True:
        time.sleep(0.1)
        t = msg_count * 0.01
        
        msg = {
            "time": time.time(),
            "position": {"x": np.sin(t), "y": np.cos(t)},
            "velocity": {"x": np.sin(2*t), "y": np.cos(2*t)}
        }
        msg_json = json.dumps(msg)
        
        result = client.publish(topic, msg_json)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            # print(f"Send `{msg_json}` to topic `{topic}`")
            pass
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1



def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    client.loop_stop()


if __name__ == '__main__':
    run()
