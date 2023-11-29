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
        self.messages_.append (Message ("Text", message))

def broadcast (message):
    print (message.decode ('ascii'))   # TODO remove, is only here for testing
    msgObj = pickle.dumps (Message ("", message))

    for client in connectedClients:
        client.send (msgObj)

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
                login = False
                accountExists = False

                for account in allUsers:
                    if (account.getUsername() == msgContents[0]) and (account.getPassword() == msgContents[1]):
                        # Successful sign in
                        confirmObj = pickle.dumps (Message ("LoginConfirm", ""))
                        client.send (confirmObj)

                        # Broadcast the login.
                        print (f'Username of client is {account.getUsername ()}.')

                        index = connectedClients.index (client)
                        usernames[index] = account.getUsername ()

                        broadcastObj = pickle.dumps (Message ("", f'   -->{account.getUsername()} has joined the chat.'))
                        #broadcast (f'   -->{usernames[index]} has joined the chat.'.encode('ascii'))
                        #TODO: talk to alex about this: all messages sent must be a message object
                        broadcast (broadcastObj)

                        ackObj = pickle.dumps (Message ("ACK", "Connected to server."))
                        client.send (ackObj)

                        # No need to look further. :)
                        login = True
                        accountExists = True
                        break
                    elif (account.getUsername () == msgContents [0]):
                        accountExists = True
                        break

                # If no login is found after looking through all the accounts, there was a login failure.
                if accountExists == False:
                    denyObj = pickle.dumps (Message ("LoginFailure", "This account does not exist."))
                    client.send (denyObj)
                    print ("Sign-in failure.")
                elif login == False and accountExists == True:
                    denyObj = pickle.dumps(Message("LoginFailure", "Incorrect password."))
                    client.send(denyObj)
                    print("Sign-in failure.")

            if (message.getType () == "CreateAccount"):
                # Add the user to the connected clients list.
                allUsers.append (Account (msgContents[0], msgContents[1]))
                confirmation = pickle.dumps (Message ("CreateConfirm", ""))
                client.send (confirmation)

                # Set the username in the usernames list.
                index = connectedClients.index (client)
                usernames[index] = msgContents[0]

            broadcast (msgContents[0].encode ('ascii')) # TODO: Broadcast is only temporary and for testing

        except Exception as e:
            print (e)

            # TODO: talk to alex about this -> not all connections may be logged in! maybe add a TTL to each thread?
            # TODO: remove usernames list (no use for it)?
            index = connectedClients.index (client)
            connectedClients.remove (client)
            username = usernames[index]
            print (f'{username} lost connection.')
            broadcast (f'{username} left the chat.'.encode ('ascii'))
            usernames.remove (username)

            client.close ()
            break

# Constantly checks for new connections.
# When a new connection is made, start a thread for that client.
def receive ():
    while True:
        client, address = server.accept ()
        print (f"Connected with {str (address)}")

        connectedClients.append (client)
        usernames.append (address)          # Default nickname is the IP address

        # Problem: the server immediate asks for a username upon a secure
        # connection with the client; however, the client must take the time to
        # login.
        # Solution: Remove the username array (we don't even need it since the
        # username is stored in the allusers list).

        # while (username == ""):
        #     requestUsernameObj = pickle.dumps (Message ("NameQuery", ""))
        #     client.send (requestUsernameObj)
        #
        #     # Exception handler because received object may be a null object.
        #     try:
        #         recvObj = pickle.loads (client.recv (1024))
        #     except:
        #         continue
        #
        #     print (recvObj.getType ())
        #
        #     # The only responses at the login screen (because we're stuck at the login screen
        #     # thus far) is a message containing the username or a request for login validation.
        #     if (recvObj.getType () == ""):
        #         username = recvObj.getContents ()
        #         connectedClients.append (client)
        #
        #         if username != "":
        #             usernames.append (username)
        #     elif (recvObj.getType () == "LoginReq"):
        #       pass
        #     print (username)


        # Delay this until the login of the user.
        # print (f'Username of client is {username}.')
        # broadcast (f'   -->{username} has joined the chat.'.encode ('ascii'))
        #
        # confirm = pickle.dumps (Message ("ACK", "Connected to server."))
        # client.send (confirm)

        thread = threading.Thread (target=handle, args=(client,))
        thread.start ()

# Function Calls
print ("[+] Server is listening...")
receive ()
