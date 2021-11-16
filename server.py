import paho.mqtt.client as mqtt

def onConnect(client, userdata, flags, rc):
    print("Connected with result code {}", rc)
    client.subscribe(a)

def onMessage(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

client = mqtt.Client()
client.on_connect = onConnect
client.on_message = onMessage
client.connect("broker.emqx.io", 1883, 60)
client.loop_forever()
