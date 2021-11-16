import paho.mqtt.client as mqtt
import time
import uuid

id = uuid.uuid4().hex
print('Your id: ', id)
chatWithID = ''

def onConnect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def onMessage(client, userdata, msg):
    print('message from {}: {}', msg.payload[0:32], msg.payload[32:])

client = mqtt.Client()
client.on_connect = onConnect
client.on_message = onMessage
client.connect("broker.emqx.io", 1883, 60)

print('`exit` to exit program')
print('Use #\{id\} to set chat with user with id')
while (1):
    client.subscribe(id)
    message = input(">>")
    if message == 'exit':
        exit()
    if message[0] == '#':
        chatWithID= message[1:]
        print('now sending messages to ', message[1:])
    else:
        if chatWithID == '':
            print('enter id to chat with')
            continue
        message = id + '/' + message
        client.publish(chatWithID, payload=message, qos=0, retain=False)

client.loop_forever()
