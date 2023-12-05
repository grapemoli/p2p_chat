import socket
import threading
import pickle
import traceback
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from message import Message

playSound = "" # Refers to the key in the self.sounds directory.

####################################
# Class: Worker
# Takes care of checking for SFX in the GUI.
####################################
class Worker (QObject):
    end = pyqtSignal ()
    sfx = pyqtSignal ()

    def run (self):
        if playSound != "":
            self.sfx.emit ()
        self.end.emit ()


####################################
# Class: Client
# The GUI for the Client.
####################################
class Client (QMainWindow):
    username = ""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('50.90.134.19', 25565))

    ####################################
    # Initialization
    ####################################
    def __init__ (self):
        super().__init__ ()

        # Initialize proper data structures.
        self.allUserId = []
        self.chatHistory = ""
        self.messageTextBox = QLineEdit ()
        self.writing = False
        self.closeChat = False
        self.selectChatButtonList = []      # The users who are already represented with a button.

        # Set the window properties (title and initial size)
        self.setWindowTitle ("ChatBocks Login")
        self.setGeometry (100, 100, 400, 300)  # (x, y, width, height)

        # Main window: holds the stack of other layouts to provide a single-page
        # application that hosts multiple UIs (as opposed to opening a lot of new
        # windows for each UI).
        self.mainWindow = QWidget ()
        self.stack = QStackedLayout ()
        self.mainWindow.setLayout (self.stack)
        self.setCentralWidget (self.mainWindow)

        # Create the other UI's and put them in a list to keep track of them. This
        # list is also what we use to switch between the UI's.
        self.loginWidget = QWidget ()
        self.addAccountWidget = QWidget ()
        self.chatWidget = QWidget ()                # Must be made dynamically before every display ()
        self.selectChatWidget = QWidget ()          # Must be made dynamically before every display ()

        self.setupUI ()

        self.stack.addWidget (self.loginWidget)
        self.stack.addWidget (self.addAccountWidget)
        self.stack.addWidget (self.selectChatWidget)
        self.stack.addWidget (self.chatWidget)

        # Create sounds.
        self.sounds = {
            'poke': QSoundEffect ()
        }

        rootDir = os.path.abspath (os.path.dirname (__file__))
        soundPath = os.path.join (rootDir, "Audio", "poke.wav")
        print(soundPath)

        self.sounds.get ('poke').setSource (QUrl.fromLocalFile (soundPath))
        self.SFXThread = QThread ()
        self.SFXWorker = Worker ()
        self.SFXWorker.moveToThread (self.SFXThread)
        self.SFXThread.started.connect (self.SFXWorker.run)
        self.SFXWorker.sfx.connect (self.play)
        self.SFXWorker.end.connect (self.SFXThread.quit)

        # Begin the display at the login page.
        self.configureButtons ()
        self.display (0)


    ####################################
    # UI-Switching Methods
    ####################################
    def display (self, index):
        # For switching between different UIs with only one window, we simply
        # change to the UI's corresponding index in self.stack.

        # Cleansing.
        self.newUsernameInput.clear ()
        self.newPasswordInput.clear ()
        self.usernameInput.clear ()
        self.passwordInput.clear ()
        self.addAccountValidationLabel.clear ()
        self.loginValidationLabel.clear ()
        self.messageTextBox.clear ()

        # Change the window title based on the UI we switch to.
        if index == 0:
            self.setWindowTitle ('ChatBox Login')
        elif index == 1:
            self.setWindowTitle ('Create an Account')
        elif index == 2:
            self.updateSelectChat ()
            self.chatHistory = ""
            self.chatRecipient = ""
            self.updateChatDisplay ()
            self.selectChatWidget.update ()
            self.setWindowTitle ('Select a Chat')
        elif index == 3:
            self.updateChatDisplay ()
            self.selectChatWidget.update ()

            if self.chatRecipient == "General":
                self.pokeButton.hide ()
                self.setWindowTitle ("General's ChatBocks")
            else:
                self.pokeButton.show ()
                userIndex = int(self.chatRecipient)

                if userIndex == self.allUserId[userIndex - 1][0]:
                    userIndex -= 1

                self.setWindowTitle (f"{self.username} & {self.allUserId[userIndex][1]} 's ChatBocks")

        self.stack.setCurrentIndex (index)

    def configureButtons (self):
        # Configures all the buttons that will "change the UI." The configuration is
        # done here because the UI needs to be loaded before it can reference another UI; however,
        # there may be circular dependencies! So, we create the UI's first (and seperately), before
        # adding the button functionality here.
        self.toAddAccountButton.clicked.connect (lambda: self.display (1))                  # Change UI.
        self.toAddAccountButton.clicked.connect (lambda: self.newUsernameInput.setText('')) # Sanitize text boxes.
        self.toAddAccountButton.clicked.connect (lambda: self.newPasswordInput.setText(''))

        self.toLoginButton.clicked.connect (lambda: self.display (0))                       # Change UI..
        self.toLoginButton.clicked.connect (lambda: self.usernameInput.clear())             # Sanitize text boxes.
        self.toLoginButton.clicked.connect (lambda: self.passwordInput.clear())


    ####################################
    # UI Setups
    ####################################
    def setupUI (self):
        self.loginWidgetUI ()
        self.addAccountWidgetUI ()
        self.chatWidgetUI ()

    def updateSelectChat (self):
        latestUser = self.selectChatButtonList [-1]

        if latestUser == "General":
            if len (self.selectChatButtonList) == 1:
                for i in range (0, len (self.allUserId)):
                    # Make a button for them, because a button does not exist.
                    user = self.allUserId[i]
                    buttonName = f'selectChatButton{user[0]}'
                    selectChatButton = QPushButton()
                    selectChatButton.setText(f'Chat with {user[1]}')
                    selectChatButton.clicked.connect(self.selectChat)
                    selectChatButton.setObjectName(buttonName)
                    self.selectChatLayout.addWidget(selectChatButton)
                    self.selectChatButtonList.append(user[0])
        else:
            for i in range (latestUser - 1, len (self.allUserId)):
                user = self.allUserId [i]
                if user[0] not in self.selectChatButtonList:
                    # Make a button for them, because a button does not exist.
                    buttonName = f'selectChatButton{user[0]}'
                    selectChatButton = QPushButton ()
                    selectChatButton.setText(f'Chat with {user[1]}')
                    selectChatButton.clicked.connect (self.selectChat)
                    selectChatButton.setObjectName (buttonName)
                    self.selectChatLayout.addWidget (selectChatButton)
                    self.selectChatButtonList.append (user[0])

        self.selectChatWidget.update ()

    def loginWidgetUI (self):
        # This is the UI for the login widget initialized in the initializer.
        # Login form label.
        layout = QGridLayout()

        # Username input.
        usernameLabel = QLabel ('<font size="4"> Username </font>')
        self.usernameInput = QLineEdit()
        self.usernameInput.setPlaceholderText ('Please enter a username')
        layout.addWidget (usernameLabel, 0, 0)
        layout.addWidget (self.usernameInput, 0, 1)

        # Password input.
        passwordLabel = QLabel ('<font size="4"> Password </font>')
        self.passwordInput = QLineEdit ()
        self.passwordInput.setPlaceholderText( 'Please enter a password')
        layout.addWidget (passwordLabel, 1, 0)
        layout.addWidget (self.passwordInput, 1, 1)

        # Login Button or Enter action configuration.
        self.usernameInput.returnPressed.connect (self.login)
        self.passwordInput.returnPressed.connect (self.login)

        loginButton = QPushButton ('Login')
        loginButton.clicked.connect (self.login)
        layout.addWidget (loginButton, 2, 0, 1, 2)
        layout.setRowMinimumHeight (2, 75)

        # Button to create account page.
        self.toAddAccountButton = QPushButton ()
        self.toAddAccountButton.setText ('Go To Add Account')
        layout.addWidget (self.toAddAccountButton)

        # For validation (it disappears once you start typing).
        self.loginValidationLabel = QLabel ()
        layout.addWidget (self.loginValidationLabel)

        self.loginWidget.setLayout (layout)

    def addAccountWidgetUI (self):
        # This is the UI for the addAccount widget.
        # Login form label.
        layout = QGridLayout ()

        # Username input.
        newUsernameLabel = QLabel ('<font size="4"> Username </font>')
        self.newUsernameInput = QLineEdit ()
        self.newUsernameInput.setPlaceholderText ('Please enter a username')    # No unique checking
        layout.addWidget (newUsernameLabel, 0, 0)
        layout.addWidget (self.newUsernameInput, 0, 1)

        # Password input.
        newPasswordLabel = QLabel ('<font size="4"> Password </font>')
        self.newPasswordInput = QLineEdit()
        self.newPasswordInput.setPlaceholderText ('Please enter a password')    # No password checking
        layout.addWidget (newPasswordLabel, 1, 0)
        layout.addWidget (self.newPasswordInput, 1, 1)

        # Register Button or Enter action configuration.
        self.newUsernameInput.returnPressed.connect (self.addAccount)
        self.newPasswordInput.returnPressed.connect (self.addAccount)

        addAccountButton = QPushButton ('Add Account')
        addAccountButton.clicked.connect (self.addAccount)
        layout.addWidget (addAccountButton, 2, 0, 1, 2)
        layout.setRowMinimumHeight (2, 75)

        # Button to create login page.
        self.toLoginButton = QPushButton ()
        self.toLoginButton.setText ('Go To Login')
        layout.addWidget (self.toLoginButton)

        # For validation (it disappears once you start typing).
        self.addAccountValidationLabel = QLabel ()
        layout.addWidget (self.addAccountValidationLabel)

        self.addAccountWidget.setLayout (layout)

    def selectChatWidgetUI (self):
        self.selectChatLayout = QVBoxLayout ()

        # TODO make scrollable

        # Make the general chat button.
        buttonName = f'selectChatButtonGeneral'
        selectChatButton = QPushButton ()
        selectChatButton.setText (f'Chat with General')
        selectChatButton.clicked.connect (self.selectChat)
        selectChatButton.setObjectName (buttonName)
        self.selectChatLayout.addWidget (selectChatButton)
        self.selectChatButtonList.append ('General')

        # Make buttons with the userID appended at the end.
        for user in self.allUserId:
            buttonName = f'selectChatButton{user[0]}'
            selectChatButton = QPushButton ()
            selectChatButton.setText (f'Chat with {user[1]}')
            selectChatButton.clicked.connect (self.selectChat)
            selectChatButton.setObjectName (buttonName)
            self.selectChatLayout.addWidget (selectChatButton)
            self.selectChatButtonList.append(user[0])

        self.selectChatWidget.setLayout (self.selectChatLayout)

    def chatWidgetUI (self):
        # This is the UI for the chatWidget.
        # Arrangement of the widgets
        layout = QVBoxLayout ()
        layoutTextInput = QGridLayout ()
        buttonLayout = QGridLayout ()

        # Make back button.
        backButton = QPushButton ()
        backButton.setText ("BACK")
        backButton.clicked.connect (self.backToSelectChat)
        buttonLayout.addWidget (backButton, 0, 0, 1, 1)

        # Make poke button.
        self.pokeButton = QPushButton ()
        self.pokeButton.setText (f'POKE')
        self.pokeButton.clicked.connect (self.poke)
        buttonLayout.addWidget (self.pokeButton, 0, 1, 1, 1)

        layout.addLayout (buttonLayout)

        # Chatbox displays all sent and received messages.
        self.chatBox = QLabel ()
        self.chatBox.setWordWrap (True)  # Wrap long messages

        # Configure the chatbox display, ONLY, to be scrollable.
        self.chatScroll = QScrollArea()
        self.chatScroll.setHorizontalScrollBarPolicy (Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.chatScroll.setVerticalScrollBarPolicy (Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.chatScroll.setWidgetResizable (True)
        self.chatScroll.setWidget (self.chatBox)
        layout.addWidget (self.chatScroll)

        # This keeps the scroller at the bottom.
        self.chatScroll.verticalScrollBar ().setValue (self.chatScroll.verticalScrollBar ().maximum ())

        # Text box area.
        self.messageTextBox = QLineEdit ()
        self.messageTextBox.font().setPointSize (18)
        self.messageTextBox.setPlaceholderText ("Type your message...")

        # Configure the enter button and the enter action.
        self.messageTextBox.returnPressed.connect (self.writeMessage)
        self.sendButton = QPushButton ()
        self.sendButton.setText ("Enter")
        self.sendButton.clicked.connect (self.writeMessage)

        # Format the elements in a line.
        layoutTextInput.addWidget (self.messageTextBox, 0, 0)
        layoutTextInput.addWidget (self.sendButton, 0, 1)

        # Set the layout for the central widget
        layout.addLayout (layoutTextInput)
        self.chatWidget.setLayout (layout)


    ####################################
    # Event Handlers
    ####################################
    def login (self):
        self.loginValidationLabel.clear ()

        # Send a request to the server about the username and password inputted.
        if self.usernameInput.text () != "" and self.passwordInput.text () != "":
            self.write ()

            # Make the client wait for us to receive the reply from the server before
            # doing anything.
            self.awaitLoginEvent = threading.Event ()
            self.awaitLoginEvent.wait (timeout=5)

            # When the receiver thread has received the server's response...
            if self.awaitLoginEvent.isSet ():

                # ...let the user log into the application if they have
                # valid credentials!
                if self.username != "":
                    self.selectChatWidgetUI ()
                    self.display (2)
        else:
            if self.usernameInput.text () == "":
                self.loginValidationLabel.setText ('Please input a username!')
            elif self.passwordInput.text () == "":
                self.loginValidationLabel.setText ('Please input a password!')

    def addAccount (self):
        self.addAccountValidationLabel.clear ()

        # Send a request to the server about the username and password inputted.
        if self.newUsernameInput.text () != "" and self.newPasswordInput.text () != "":
            self.write ()

            # Make the client wait for the reply from the server before doing anything.
            self.awaitAddUserEvent = threading.Event ()
            self.awaitAddUserEvent.wait (timeout=5)

            # Once we receive the reply from the server...
            if self.awaitAddUserEvent.isSet():

                # ...if the account is successfully made, return the user to the
                # login screen. We require the user to log in. >:)
                if self.username != "":
                    self.display (0)
                    self.username = ""
        else:
            if self.newUsernameInput.text () == "":
                self.addAccountValidationLabel.setText ('Please input a username!')
            elif self.newPasswordInput.text () == "":
                self.addAccountValidationLabel.setText ('Please input a password!')

    def updateChatDisplay (self):
        # This is for live chat updates.
        self.chatBox.clear ()
        self.chatBox.setText (self.chatHistory)
        self.chatWidget.update ()

        # This keeps the scroll bar of the chatbox from riding up with new chats.
        self.chatScroll.verticalScrollBar ().setValue (self.chatScroll.verticalScrollBar ().maximum ())

    def selectChat (self):
        button = self.sender()
        buttonName = str (button.objectName())

        # Since the userId is appended onto the button with format
        # selectChatButton{userId}, we can parse the user id.
        self.chatRecipient = buttonName[16:]

        if (self.chatRecipient == "General"):
            self.write ()
            self.display (3)
            print (f'Chatting with General')
        else:
            self.write ()

            # Place an event, waiting for the server to respond.
            self.awaitSelectChatEvent = threading.Event ()
            self.awaitSelectChatEvent.wait (timeout=5)

            # When the receiver thread has received the server's response...
            if self.awaitSelectChatEvent.isSet ():
                # If the event set, switch to the chat display and update the
                # chat history to include the past messages.
                self.display (3)
                print (f'Chatting with user#{self.chatRecipient}')
            else:
                print ("Timeout while waiting for server for DM information")


    def backToSelectChat (self):
        # Send a closed DM request to the server, waiting.
        # for the server response.
        self.closeChat = True

        self.write ()
        self.awaitCloseChat = threading.Event ()
        self.awaitCloseChat.wait (timeout=5)

        if (self.awaitCloseChat.isSet ()):
            self.chatRecipient = ""

            self.closeChat = False
            self.display (2)

    def writeMessage (self):
        if self.messageTextBox.text () != "":
            self.write ()

    def poke (self):
        print (f'poked {self.chatRecipient}')
        global playSound
        playSound = 'poke'
        self.write ()

    def play (self):
        # Upon playing the sound, reset the play sound attribute.
        global playSound
        self.sounds.get (playSound).play ()

        playSound = ""

    def writeMessage (self):
        self.writing = True

        if self.messageTextBox.text () != "":
            self.write ()


    ####################################
    # Thread-Related Methods
    ####################################
    def receive (self):
        # This method is continuously run by a thread to prevent the GUI from freezing.
        # Because the main thread is the only thread that is allowed to manipulate the GUI,
        # certain responses from the server that require GUI changes will use Events.
        # Please refer to the appropriate event handler method to see how these Events are
        # applied.

        # Always looking for server messages.
        while True:
            try:
                # Unserialize the server's message.
                msgObject = pickle.loads (self.client.recv (1024))
                type = msgObject.getType ()
                message = msgObject.getContents ()

                # Different types of messages require different actions.
                if type == 'Text':
                    # Your typical message between users.
                    self.chatHistory += (message[0])
                    self.updateChatDisplay ()
                elif type == 'DMConfirm':
                    self.chatHistory = ""

                    for msg in message:
                        self.chatHistory += msg.getContents()[0]

                    self.awaitSelectChatEvent.set ()
                elif type == 'CloseChat':
                    self.allUserId = message
                    self.awaitCloseChat.set ()
                elif type == 'LoginConfirm':
                    # The server has confirmed that the user has a successful
                    # login.
                    self.username = self.usernameInput.text ()
                    self.allUserId = message

                    print (f'logged in as {self.username}')

                    # Release the client's wait on the server to reply.
                    self.awaitLoginEvent.set ()
                elif type == 'LoginFailure':
                    self.loginValidationLabel.setText (message)
                    self.awaitLoginEvent.set ()
                elif type == 'CreateConfirm':
                    self.username = self.newUsernameInput.text ()
                    self.awaitAddUserEvent.set ()
                elif type == 'CreateFailure':
                    self.addAccountValidationLabel.setText (message)
                    self.awaitAddUserEvent.set ()
                elif type == 'Poke':
                    global playSound
                    playSound = 'poke'

                    self.SFXThread.start ()
                    print (f'Got poked by {message[0]}')
                else:
                    pass
            except Exception as e:
                # Any failure will forcibly close the connection.
                print (e)
                print (traceback.format_exc())
                self.client.close ()
                break

    def write (self):
        # This method is handled by a thread to prevent the GUI from freezing.
        # Note that this method is NOT continuously looking for messages to send to
        # the server. This is because this method is treated like an event handler--
        # it's only called when a message needs to be sent after some button click.

        # Messages that can be sent if the user is not logged in are login and create account
        # messages.

        if self.username == "":
            # Login: does the user exist and do they have the right credentials?
            if self.usernameInput.text () != "" and self.passwordInput.text () != "":
                # Send the serialized message.
                message = [self.usernameInput.text (),self.passwordInput.text ()]
                loginObj = pickle.dumps (Message ("LoginReq", message))
                self.client.send (loginObj)

            # Account Creation: is the account the user is trying to make valid?
            elif self.newUsernameInput.text() != "" and self.newPasswordInput.text () != "":
                message = [self.newUsernameInput.text (),self.newPasswordInput.text ()]
                createObj = pickle.dumps (Message ("CreateAccount", message))
                self.client.send (createObj)

        # The client can only send these type of messages to the server if the user is logged in.
        # This acts as a privilege scoping.
        elif self.username != "":
            global playSound
            # Messages to other user(s).
            if playSound == 'poke':
                pokeObj = pickle.dumps(Message("Poke", self.chatRecipient))
                self.client.send(pokeObj)
                playSound = ''
            elif self.writing == True:
                message = [f'{self.username}: {self.messageTextBox.text ()}\n']
                messageObj = pickle.dumps (Message ("Text", message))
                self.client.send (messageObj)
                self.writing = False

                # Sanitize.
                self.messageTextBox.clear ()
            else:
                # Closing the chat.
                if self.closeChat == True:
                    message = ["null"]
                    messageObj = pickle.dumps (Message ('CloseChat', message))
                    self.client.send (messageObj)
                # User moves to to general chat.
                elif self.chatRecipient == "General":
                    messageObj = pickle.dumps (Message ('SwitchToGeneral', []))
                    self.client.send (messageObj)
                # If the user exists a non-general chat.
                elif self.chatRecipient != "":
                    message = [self.chatRecipient]
                    messageObj = pickle.dumps (Message ('SwitchToDM', message))
                    self.client.send (messageObj)


    def start (self):
        # Thread starts and configurations.
        receive_thread = threading.Thread (target=self.receive)
        receive_thread.start ()

        write_thread = threading.Thread (target=self.write)
        write_thread.start ()