import json
import socket
import paho.mqtt.client as paho

# Name of this client. Don't use identical client IDs for different clients
import time

clientID = 'GS'
DEBUG = 0
TOPIC = 'GS_TOPIC'
DRONE_IP = '192.168.1.102'


class MosquittoEndpoint:
    def __init__(self):
        self.mqttc = paho.Client(client_id=clientID, clean_session=True)
        self.mqttc.on_connect = self.onConnect
        self.mqttc.on_subscribe = self.onSubscribe
        self.mqttc.on_message = self.onMessage
        self.mqttc.on_disconnect = self.onDisconnect
        self.mqttc.connect("192.168.1.102", 1883, 60)
        self.mqttc.subscribe(TOPIC)

    def onConnect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    def onSubscribe(self, client, userdata, mid, granted_qos):
        print('Subscribed on topic.')

    def onMessage(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        msg = json.loads(payload.replace('\'', '\"'))
        print('Message Received ' + payload)
        if msg['type'] == 'video_ready_for_transmit':
            fetchVideo(msg['name'])
            self.mqttc.publish("videoProcessing", payload='{"status": "finish"}')

    def onDisconnect(self, client, userdata, message):
        print("Disconnected from the broker.")

    def sendCommand(self, topic, payload):
        self.mqttc.publish(topic, payload=payload, qos=1, retain=False)


def fetchVideo(name='launch'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('File transmission socket opened')
    while True:
        try:
            s.connect(('192.168.1.102', 30000))
            with open('static/videos/' +    name + '.mp4', 'wb') as f:
                while True:
                    data = s.recv(1024)
                    if not data:
                        break
                    f.write(data)
            break
        except:
            continue

    f.close()
    s.close()
    print('File transmission socket finished')



mosqEndpoint = MosquittoEndpoint()
mosqEndpoint.mqttc.loop_start()
time.sleep(1000)
