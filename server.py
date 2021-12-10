import paho.mqtt.client as mqtt

users = []

# Sends error to client
def error(id, error):
    client.publish(id, payload='error/' + error)

# Finds the public key for a given id
def getPublicKey(id):
    for user in users:
        if user['id'] == id:
            return user['publicKey']
    return ' '

# Used to parse the data recieved from the client
def parse(receivedMessage):
    global users
    params = receivedMessage.split('/')
    #if len(params) < 2:
    #    client.publish(params[1], payload=str(publicKey), retain=False)
    if params[0] == 'newUser':
        # key gets split into multiple pieces in the list since the request string is split by the '/' delimeter, this loops through to append all the split segments together
        key = ''
        for param in params[2:]:
            key = key + '/' + param
        user = {'id': params[1], 'publicKey': key}
        users.append(user)
        print('New user added: ', user)
    if params[0] == 'getPublicKey':
        publicKey = getPublicKey(params[2])
        if publicKey == ' ':
            error('server: finding public key', params[1])
            return
        client.publish(params[1], payload='publicKey/' + publicKey)
    if params[0] == 'message':
        b64message = params[3]
        for param in params[4:]:
            b64message = b64message + '/' + param
        client.publish(params[2], payload = 'message/' + params[1] + '/' + b64message)


def onConnect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe("server")

def onMessage(client, userdata, msg):
    parse((msg.payload).decode())

client = mqtt.Client()
client.on_connect = onConnect
client.on_message = onMessage
client.connect("broker.emqx.io", 1883, 60)
client.loop_forever()
