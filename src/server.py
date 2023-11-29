import socket
import traceback
import pickle
import threading
from message import Message

host = '0.0.0.0'
port = 25565

server = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
server.bind ((host, port))
server.listen ()

connectedClients = []
usernames = []

# List holds all accounts
allUsers = []

# List holds all dms
DMs = []

class Account (object):
    def __init__ (self, username, password):
        # Username to identify users.
        self.username_ = username

        # Password for each user. May change.
        self.password_ = password

        # ID of each user:
        # Keeps track of messages when username is changed.
        # (userID should never change)
        # Assign ID of last user + 1.
        self.userID = len (allUsers)
        allUsers.append (self)

    def getUsername (self):
        return self.username_
    
    def getPassword (self):
        return self.password_
    
    def getUserID (self):
        return self.userID
    
# Holds dm and message history between 2 users
class DM (object):
    def __init__ (self, user1, user2):
        # Set the userPair.
        # Pair of IDs (ints) in a tuple (immutable).
        self.userPair_ = {user1, user2}

        # Initialize the messages.
        self.messages_ = []

    def newMessage (self, senderID, message):
        self.messages_.append(Message ("Text", message))

def broadcast (message):
    print (message.decode ('ascii'))   # TODO remove, is only here for testing

    for client in connectedClients:
        client.send (message)

# Runs in a thread, constantly checks if the client has sent a new message
def handle (client):
    user = None
    while True:
        try:
            # What do we do with the client's message?
            message = pickle.loads (client.recv (1024))
            msgContents = message.getContents ().split (',')

            # Different types of messages require different methods of handling
            if message.getType () == "LoginReq":
                for account in allUsers:
                    if (account.getUsername() == msgContents[0]) and (account.getPassword() == msgContents[1]):
                        # Successful sign in
                        user = account
                        confirmation = pickle.dumps (Message ("LoginConfirm", ""))
                        client.send (confirmation)
                    else:
                        # Bad username or password
                        print ("Sign-in failure.")

            if (message.getType () == "CreateAccount"):
                allUsers.append (Account (msgContents[0], msgContents[1]))
                confirmation = pickle.dumps (Message ("CreateConfirm", ""))
                client.send (confirmation)

            # TODO: remove broadcast
            broadcast(msgContents[0].encode ('ascii')) # Broadcast is only temporary and for testing

        except Exception as e:
            print (e)
            index = connectedClients.index (client)
            connectedClients.remove (client)
            client.close ()
            username = usernames[index]
            print (f'{username} lost connection.')
            broadcast (f'{username} left the chat.'.encode ('ascii'))
            usernames.remove (username)
            break

# Constantly checks for new connections.
# When a new connection is made, start a thread for that client.
def receive ():
    while True:
        client, address = server.accept ()
        print (f"Connected with {str (address)}")

        username = ""

        # Problem: the server immediate asks for a username upon a secure
        # connection with the client; however, the client must take the time to
        # login. The complex but time & network-efficient method is to use an async
        # method; however, that's complex in Python. So, we opt to keep asking the
        # client for a username message until the username returned is not "".
        while (username == ""):
            client.send ('NameQuery'.encode ('ascii'))
            username = client.recv (1024).decode ('ascii')
            usernames.append (username)
            connectedClients.append (client)

        print (f'Username of new client is {username}.')
        broadcast (f'   -->{username} has joined the chat.'.encode ('ascii'))
        client.send ('Connected to the server.'.encode ('ascii'))

        thread = threading.Thread (target=handle, args=(client,))
        thread.start ()

print ("[+] Server is listening...")
receive ()
