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

# This list holds all the accounts.
allUsers = []

# This list holds all the DMs.
DMs = []


########################################################################
# Class: Account
########################################################################
class Account (object):
    ####################################
    # Initialization
    ####################################
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


    ####################################
    # Methods
    ####################################
    def getUsername (self):
        return self.username_
    
    def getPassword (self):
        return self.password_
    
    def getUserID (self):
        return self.userID


########################################################################
# Class: DM
# Holds DM and message history between 2 users.
########################################################################
class DM (object):
    ####################################
    # Initialization
    ####################################
    def __init__ (self, user1, user2):
        # Set the userPair.
        # Pair of IDs (ints) in a tuple (immutable).
        self.userPair_ = {user1, user2}

        # Initialize the messages.
        self.messages_ = []

    ####################################
    # Method
    ####################################
    def newMessage (self, senderID, message):
        self.messages_.append (Message ("Text", message))



########################################################################
# Server Methods!
########################################################################
def broadcast (message):
    # Send a message to all the existing users who are currently connected
    # to the server.
    msgObj = pickle.dumps (Message ("", message))

    for client in connectedClients:
        client.send (msgObj)

def handle (client):
    # Runs in a thread, constantly checks if the client has sent a new message
    user = None
    while True:
        try:
            # What do we do with the client's message?
            message = pickle.loads (client.recv (1024))
            msgContents = message.getContents ()

            # Different types of messages require different methods of handling.
            if message.getType () == '':            # TODO: will need to add a recipient section in the message
                                                    # TODO:  to send the message to the recipient
                                                    # TODO: for many-to-many, give each DM a uid
                # TODO: implement this
                # The user sends a message to the server. The server saves the message in the appropriate
                # DM class, and sends the to the recipients INCLUDING THE USER.
                # Or--even better--each DM class has its own broadcast() function that sends to IT'S recipients
                broadcast (msgContents)
                print (f'msg: {msgContents}')       # TODO: delete

            if message.getType () == "LoginReq":
                msgContents = msgContents.split (',')
                login = False
                accountExists = False

                for account in allUsers:
                    if (account.getUsername() == msgContents[0]) and (account.getPassword() == msgContents[1]):
                        # Successful sign in. Send the confirmation response to the user.
                        confirmObj = pickle.dumps (Message ("LoginConfirm", ""))
                        client.send (confirmObj)

                        # Broadcast the login.
                        print (f'Username of client is {account.getUsername ()}.')
                        broadcast(f'   -->{account.getUsername()} has joined the chat.')

                        # Fetch and update the client's information to match the Account on file.
                        index = connectedClients.index (client)
                        usernames[index] = account.getUsername ()

                        # This response is for the user to see a confirmation in their UI.
                        ackObj = pickle.dumps (Message ("ACK", "Connected to server."))
                        client.send (ackObj)

                        # Since we already found the account, we can break early. :)
                        login = True
                        accountExists = True
                        break
                    elif (account.getUsername () == msgContents [0]):
                        # This means the user must have typed the wrong password to an
                        # existing account.
                        accountExists = True
                        break

                # If no login is found after looking through all the accounts, there was a login failure.
                # Update the contents of the server response based on the *type* of login failure.
                if accountExists == False:
                    denyObj = pickle.dumps (Message ("LoginFailure", "This account does not exist."))
                    client.send (denyObj)
                    print ("Sign-in failure: Account does not exist")
                elif login == False and accountExists == True:
                    denyObj = pickle.dumps (Message("LoginFailure", "Incorrect password."))
                    client.send (denyObj)
                    print ("Sign-in failure: Wrong Password")

            if (message.getType () == "CreateAccount"):
                msgContents = msgContents.split(',')

                # Add the user to the connected clients list.       #TODO: validation! for now, all accounts are added
                allUsers.append (Account (msgContents[0], msgContents[1]))
                confirmation = pickle.dumps (Message ("CreateConfirm", ""))
                client.send (confirmation)

                # Set the username of the client in the usernames list.
                index = connectedClients.index (client)
                print (f'Account created: {usernames[index]} nicknamed {msgContents[0]}')
                usernames[index] = msgContents[0]

            #broadcast (msgContents[0]) # TODO: Broadcast is only temporary and for testing--delete

        except Exception as e:
            # For any client whose connection caused something finnicky to happen (could be that
            # they exited the chat), cut their connection.
            print (e)
            index = connectedClients.index (client)
            connectedClients.remove (client)
            username = usernames[index]

            print (f'{username} lost connection.')
            broadcast (f'{username} left the chat')

            usernames.remove (username)
            client.close ()
            break

def receive ():
    # Constantly checks for new connections.
    # When a new connection is made, start a thread for that client.
    while True:
        client, address = server.accept ()
        print (f"Connected with {str (address)}")

        connectedClients.append (client)
        usernames.append (address)          # Default nickname is the IP address until a login is successful.

        thread = threading.Thread (target=handle, args=(client,))
        thread.start ()


####################################
# Function Calls (to start the server)
####################################
print ("[+] Server is listening...")
receive ()
