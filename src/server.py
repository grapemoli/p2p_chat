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

        # If the client is connected, this will contain the socket the account is associated with.
        self.currentSocket_ = None

        # Boolean. Logged in or out status
        self.isLoggedIn_ = False

        # Page the account is viewing. None if logged out
        self.pageViewing_ = None

        # ID of each user:
        # Keeps track of messages when username is changed.
        # (userID should never change)
        # Assign ID of last user + 1.
        self.userID_ = len (allUsers)
        allUsers.append (self)


    ####################################
    # Methods
    ####################################
    def getUsername (self):
        return self.username_
    
    def getPassword (self):
        return self.password_
    
    def getUserID (self):
        return self.userID_
    
    def getPage (self):
        return self.pageViewing_
    
    def getLoggedIn(self):
        return self.isLoggedIn_
    
    def getSocket(self):
        return self.currentSocket_
    
    def setLoggedIn(self, newStatus):
        self.isLoggedIn_ = newStatus

    def setSocket(self, newSocket):
        self.currentSocket_ = newSocket

    def setPage(self, newPage):
        self.pageViewing_ = newPage


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
        self.userPair_ = (user1, user2)

        # Initialize the messages.
        self.messages_ = []

    ####################################
    # Method
    ####################################
    def newMessage (self, message):
        self.messages_.append (Message ("Text", message))

    def getMessages (self):
        return self.messages_

    def getUserPair (self):
        return self.userPair_



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
            msgContents = message.getContents()

            # Different types of messages require different methods of handling.
            if message.getType () == '':
                # The user sends a message to the server. The server saves the message in the appropriate
                # DM class, and sends the to the recipients INCLUDING THE USER.
                # Or--even better--each DM class has its own broadcast() function that sends to IT'S recipients
                broadcast (msgContents[0])
                print (f'msg: {msgContents[0]}')       # TODO: delete

            if message.getType () == "LoginReq":
                login = False
                accountExists = False

                for account in allUsers:
                    if (account.getUsername() == msgContents[0]) and (account.getPassword() == msgContents[1]):
                        # Successful sign in. Send the confirmation response to the user.

                        # Thread now knows the user it is dealing with until close.
                        user = account
                        user.setLoggedIn(True)
                        user.setSocket(client)

                        # Build user list to send to client.
                        userList = []
                        for accountUser in allUsers:
                            if (accountUser != user):
                                userList.append((accountUser.getUserID () , accountUser.getUsername ()))

                        confirmObj = pickle.dumps (Message ("LoginConfirm", userList))
                        client.send (confirmObj)

                        # Broadcast the login.
                        print (f'Username of client is {account.getUsername ()}.')

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

                        # TODO: This does not acount for duplicate usernames. May want to continue instead of break. 
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

            elif (message.getType () == "CreateAccount"):

                # Add the user to the connected clients list.

                # TODO only let unique usernames be made into an account:
                ################# REFACTOR AS NEEDED ##############################
                ###### THIS WAS HAPHAZARDLY PUT TOGETHER TO TEST CLIENT
                accountExists = False

                for account in allUsers:
                    if account.getUsername() == msgContents[0]:
                        # Since we already found the account, we can break early. :)
                        accountExists = True
                        break

                # If no login is found after looking through all the accounts, the account does
                # not exist!
                if accountExists == False:
                    # Create the account and notify the user.
                    newAccount = Account (msgContents[0], msgContents[1])

                    confirmObj = pickle.dumps (Message("CreateConfirm", f'{msgContents[0]} successfully made.'))
                    client.send (confirmObj)

                    # Set the username of the client in the usernames list.
                    index = connectedClients.index( client)
                    print (f'Account created: {usernames[index]} nicknamed {newAccount.getUsername()}')
                    usernames[index] = msgContents[0]
                elif accountExists == True:
                    denyObj = pickle.dumps (Message ("CreateFailure", f'{msgContents[0]} already exists!'))
                    client.send (denyObj)

            elif (message.getType() == "SwitchToDM"):
                user.setPage(["DM", msgContents[0]])

                currentDM = None

                # If DM history between these 2 users doesn't exist, create it.
                foundDM = False

                for dm in DMs:
                    userpair = dm.getUserPair()

                    if ((int(userpair[0]) == int(user.getUserID())) and (int(userpair[1]) == int(msgContents[0]))):
                        foundDM = True
                        currentDM = dm
                        break
                    elif ((int(userpair[0]) == int(msgContents[0])) and (int(userpair[1]) == int(user.getUserID()))):
                        foundDM = True
                        currentDM = dm
                        break

                # If foundDM is still false, make the new DM.
                if (not foundDM):
                    print("making new dm")
                    currentDM = DM(user.getUserID(), msgContents[0])
                    DMs.append(currentDM)

                # Give the client the messages it needs to display.
                print(currentDM.getMessages())
                msgObj = pickle.dumps(Message("DMConfirm", currentDM.getMessages()))
                client.send(msgObj)

            elif (message.getType() == "Text"):

                # If we are viewing a DM, text needs only sent to 1 other user.
                if (user.getPage()[0] == "DM"):

                    recipient = allUsers[int(user.getPage()[1])]

                    # If recipient is logged in and viewing the page, display the message to them.
                    if (recipient.getLoggedIn() and (int(recipient.getPage()[1]) == int(user.getUserID()))):
                        recipient.getSocket().send(pickle.dumps(message))

                    # Always send message back for sender to display.
                    client.send(pickle.dumps(message))

                    # Add message to DM history. Need to find the DM first.
                    currentDM = None
                    for dm in DMs:
                        if ((int(dm.getUserPair()[0]) == int(user.getUserID())) and (int(dm.getUserPair()[1]) == int(user.getPage()[1]))):
                            currentDM = dm
                            break
                        elif ((int(dm.getUserPair()[0]) == int(user.getPage()[1])) and (int(dm.getUserPair()[1]) == int(user.getUserID()))):
                            currentDM = dm
                            break

                    currentDM.newMessage(msgContents)

            elif (message.getType() == "CloseDM"):
                # Build user list to send to client.
                userList = []
                for account in allUsers:
                    if (account != user):
                        userList.append((account.getUserID, account.getUsername))

                # Send updated list of all users to client
                dmListObj = pickle.dumps(Message ("CloseDM", userList))
                client.send(dmListObj)

                user.setPage(["DMList", None])


        except Exception as e:
            # For any client whose connection caused something finnicky to happen (could be that
            # they exited the chat), cut their connection.
            print (e)
            print (traceback.format_exc())
            index = connectedClients.index (client)
            connectedClients.remove (client)
            username = usernames[index]

            # Reset the state of that account if they were logged in
            if (user != None):
                user.setLoggedIn(False)
                user.setSocket(None)
                user.setPage(None)


            print (f'{username} lost connection.')

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
