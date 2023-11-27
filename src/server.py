import socket
import threading

host = '0.0.0.0'
port = 25565

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
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
        self.messages_.append(Message(senderID, message))

    
#structure simply holds senderID and the message sent
class Message(object):
    def __init__(self, senderID, message):
        #set senderID (int)
        self.senderID_ = senderID

        #set message (string)
        self.message_ = message

    def getSenderID(self):
        return self.senderID_
    
    def getMessage(self):
        return self.message_


def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            print(f'{username} lost connection.')
            broadcast(f'{username} left the chat.'.encode('ascii'))
            usernames.remove(username)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('NAME_QUERY'.encode('ascii'))
        username = client.recv(1024).decode('ascii')
        usernames.append(username)
        clients.append(client)

        print(f'Username of new client is {username}.')
        broadcast(f'   -->{username} has joined the chat.'.encode('ascii'))
        client.send('Connected to the server.'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server is listening...")
receive()