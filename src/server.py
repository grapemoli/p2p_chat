import socket

import pickle
import threading

host = '0.0.0.0'
port = 25565

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

connectedClients = []
usernames = []

#list holds all accounts
allUsers = []

#list holds all dms
DMs = []

class Account(object):
    def __init__(self, username, password):
        #username to identify users
        self.username_ = username

        #password for each user. may change
        self.password_ = password

        #ID of each user.
        #keeps track of messages when username is changed
        #userID should never change
        #assign ID of last user + 1
        self.userID = len(allUsers)
        allUsers.append(self)

    def getUsername(self):
        return self.username_
    
    def getPassword(self):
        return self.password_
    
    def getUserID(self):
        return self.userID
    
#holds dm and message history between 2 users
class DM(object):
    def __init__(self, user1, user2):
        #set the userPair
        #pair of IDs (ints) in a tuple (immutable)
        self.userPair_ = {user1, user2}

        #initialize the messages
        self.messages_ = []

    def newMessage(self, senderID, message):
        self.messages_.append(Message("Text", message))
    
class Message(object):
    def __init__(self, type, contents):
        #initialize members
        self.type_ = type
        self.contents_ = contents

    def getType(self):
        return self.type_
    
    def getContents(self):
        return self.contents_


def broadcast(message):
    for client in connectedClients:
        client.send(message)

#runs in a thread, constantly checks if the client has sent a new message
def handle(client):
    user = None
    while True:
        try:
            #what do we do with the client's message?
            message = pickle.loads(client.recv(1024))
            msgContents = message.getContents.split(',')

            if (message.getType() == "LoginReq"):
                for account in allUsers:
                    if ((account.getUsername() == msgContents[0]) and (account.getPassword() == msgContents[1])):
                        #successful sign in
                        user = account
                        confirmation = pickle.dumps(Message("LoginConfirm", ""))
                        client.send(confirmation)
                    else:
                        #bad username or password
                        print("sign in fail")

            if (message.getType() == "CreateAccount"):
                allUsers.append(Account(msgContents[0], msgContents[1]))
                confirmation = pickle.dumps(Message("CreateConfirm", ""))
                client.send(confirmation)
                        

            broadcast(message)
        except:
            index = connectedClients.index(client)
            connectedClients.remove(client)
            client.close()
            username = usernames[index]
            print(f'{username} lost connection.')
            broadcast(f'{username} left the chat.'.encode('ascii'))
            usernames.remove(username)
            break

#constantly checks for new connections.
#when a new connection is made, start a thread for that client
def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('NAME_QUERY'.encode('ascii'))
        username = client.recv(1024).decode('ascii')
        usernames.append(username)
        connectedClients.append(client)

        print(f'Username of new client is {username}.')
        broadcast(f'   -->{username} has joined the chat.'.encode('ascii'))
        client.send('Connected to the server.'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("[+] Server is listening...")
receive()
