import paho.mqtt.client as mqtt
import time
import uuid
import threading
import rsa
import base64

# Create user id
id = uuid.uuid4().hex
print('*****************************************************')
print('*  Your id: ', id + '       *')

# Generate user's keys
publicKey, privateKey = rsa.newkeys(512)

chatWithID = ''
chatWithPublicKey = ''
message = ''


# Sends user data to server when they connect to the server
def onConnect(client, userdata, flags, rc):
    global publicKey
    print("Connected with result code", rc)
    newUserRequest = 'newUser/' + str(id) + '/' + publicKey.save_pkcs1(format='PEM').decode()
    client.publish("server", payload = newUserRequest)
    
# handles when the client recieves data from the server
def onMessage(client, userdata, msg):
    parse((msg.payload).decode())

# initiallize the client
client = mqtt.Client()
client.on_connect = onConnect
client.on_message = onMessage
client.connect("broker.emqx.io", 1883, 60)
client.subscribe(id)

# Sends request to get a users public key to the server
def getPublicKey(getId):
    global id
    client.publish('server', payload='getPublicKey/' + id + '/' + getId)

# Encrypts string with rsa 512 bit key
def encrypt(message):
    global chatWithPublicKey
    if chatWithPublicKey == '':
        print('no public key')
        return
    return rsa.encrypt(message.encode(), chatWithPublicKey)

# Decrypts encrypted messages
def decrypt(message):
    global privateKey
    return rsa.decrypt(message, privateKey).decode()

# Used to parse the data recieved from the server
def parse(receivedPayload):
    global chatWithPublicKey
    params = receivedPayload.split('/')
    if params[0] == 'error':
        print('error: ', params[1])
    if params[0] == 'publicKey':
        # key gets split into multiple pieces in the list since the request string is split by the '/' delimeter, this loops through to append all the split segments together
        key = params[2]
        for param in params[3:]:
            key = key + '/' + param
        chatWithPublicKey = rsa.key.PublicKey.load_pkcs1(bytes(key.encode(encoding='utf-8')), format='PEM')
    if params[0] == 'message':
        b64message = params[2]
        for param in params[3:]:
            b64message = b64message + '/' + param
        encodedB64message = b64message.encode() # need to encode string for decryption
        print('Message from', params[1] + ': ' + decrypt(base64.b64decode(encodedB64message)))

# function for displaying different commands that the user can use
def help():
    print('*****************************************************')
    print('*  Use `\help` to show special commands             *')
    print('*  Use `\exit` to exit program                      *')
    print('*  Use `\id` to show your id                        *')
    print('*  Use #<id> to send messages to with the given id  *')
    print('*****************************************************')


# function built to crash the program
def crash():
    try:
        crash()
    except:
        crash()

# function for indefinetely looping for user input and processing that input
def userInputLoop():
    global chatWithID
    while True:
        message = input(">>")
        if message == '':
            userInputLoop()
        if message == '\help':
            help()
        if message == '\exit':
            crash() # because this function is ran in a thread it is not so easy to kill the thread from inside of it so this is the best makshift alternative I came up with should be TODO: fix in next update
        if message == '\id':
            print('Your id: ', id)
        if message[0] == '#':
            chatWithID= message[1:]
            print('now sending messages to ', chatWithID)
            getPublicKey(chatWithID)
        else:
            if chatWithID == '':
                print('please enter id to chat with')
                userInputLoop()
            message = encrypt(message)
            b64message = base64.b64encode(message) #encode the encryption in base64 so it can be sent to the server as a string
            messageRequest = 'message/' + id + '/' + chatWithID + '/' + b64message.decode()
            client.publish("server", payload = messageRequest) # send message to server

#function for indefinetely looping the MQTT client
def clientLoop():
    client.loop_forever()

help()

# Run the input and MQTT client loops in parralel
threading.Thread(target=clientLoop).start()
threading.Thread(target=userInputLoop).start()