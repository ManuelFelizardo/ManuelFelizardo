import json
import threading
import time
import paho.mqtt.client as paho
import memcache
import socket
from math import radians
from API import *
from converter import getCanvasPosition


def on_message_drone(mosq, obj, msg):
    mosq.disconnect()
    data = json.loads(msg.payload.decode("utf-8"))
    #print(data)
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    dict=mc.get("id")
    if(dict!=None):
        gpsList=[(dict[t],t) for t in dict]
        gyroscope=(-radians(data["angy"]),radians(data["angx"]))
        gps=(data["lat"],data["log"])
        cameraOrientation=-radians(data["ort"])
        if data["alt"]<=2:
            droneHeight=25
        else:
            droneHeight=data["alt"]
        result=getCanvasPosition(gpsList[0][0], gpsList, cameraOrientation, droneHeight, gyroscope)
        mc.set("imagePositions",result)

def on_message_boat(mosq, obj, msg):
    data = json.loads(msg.payload.decode("utf-8"))
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    dict=mc.get("id")
    if dict==None:
        dict={}
    dict[data["id"]]=(data["coords"][1],data["coords"][0])
    #print("boat gps locations: ",dict)
    mc.set("id",dict)
    publish_on_rest(data)


def publish_on_rest(dic,ip="192.168.1.103"):
    try:
        r = requests.post('http://'+ip+':5000/produce', json.dumps(dic))
    except:
        pass

def on_publish(mosq, obj, mid):
    pass

class CalculateImagePositions(threading.Thread):

    def __init__(self, on_message, on_publish):
        threading.Thread.__init__(self)
        self.on_message = on_message_drone
        self.on_publish = on_publish

    def run(self):
        while True:
            client = paho.Client(clean_session=True)
            client.on_message = self.on_message
            client.on_publish = self.on_publish
            client.connect("192.168.1.102", 1883, 60)
            client.subscribe("droneInfo", 2)
            while client.loop() == 0:
                pass


class UpdateBoatPosition(threading.Thread):

    def __init__(self, on_message, on_publish):
        threading.Thread.__init__(self)
        self.on_message = on_message_boat
        self.on_publish = on_publish

    def run(self):
        client = paho.Client()
        client.on_message = self.on_message
        client.on_publish = self.on_publish
        client.connect("192.168.1.102", 1883, 60)
        client.subscribe("id", 0)

        while client.loop() == 0:
            pass

class VideoSplitter(threading.Thread):

    def run(self):
        NUM = 4

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('0.0.0.0', 1000))
        s.sendto(b'', ('192.168.4.1', 1000))
        s.sendto(b'', ('192.168.1.102', 1000))
        while True:
            try:
                data, addr = s.recvfrom(4096*100)
                #print('Recebi')
                for i in range(0, NUM):
                    try:
                        s.sendto(data, ('127.0.0.1', 1001 +i))
                    except:
                        continue
            except:
                continue




if __name__ == '__main__':
    updateBoatPosition = UpdateBoatPosition(on_message_boat, on_publish)
    updateBoatPosition.start()
    calculateImagePositions = CalculateImagePositions(on_message_drone, on_publish)
    calculateImagePositions.start()
    videoSplitter=VideoSplitter()
    videoSplitter.start()
    #app.run(host='0.0.0.0', debug=True, threaded=True)
