import socket
import threading
import pickle
import traceback
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from message import Message

class Client (QMainWindow):
    username = ""
    client = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    client.connect (('127.0.0.1', 25565))   # TODO: 50.90.134.19


    ####################################
    # Initialization
    ####################################
    def __init__ (self):
        super().__init__ ()

        # Initialize proper data structures.
        self.allUserId = []
        self.chatHistory = ""
        self.chatRecipient = ""
        self.messageTextBox = QLineEdit ()

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

        # Begin the display at the login page.
        self.configureButtons ()
        self.display (0)


    ####################################
    # UI-Switching Methods
    ####################################
    def display (self, index):
        # For switching between different UIs with only one window, we simply
        # change to the UI's corresponding index in self.stack.
        self.stack.setCurrentIndex (index)

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
            self.setWindowTitle ('Select a Chat')
        elif index == 3:
            self.updateChatDisplay ()
            self.setWindowTitle (f"{self.username}'s ChatBocks")

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
        #self.chatWidgetUI ()

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
        layout = QVBoxLayout ()

        # TODO make scrollable

        # Make buttons with the userID appended at the end.
        if len (self.allUserId) != 0:
            for user in self.allUserId:
                buttonName = f'selectChatButton{user[0]}'
                selectChatButton = QPushButton ()
                selectChatButton.setText (f'Chat with {user[1]}')
                selectChatButton.clicked.connect (self.selectChat)
                selectChatButton.setObjectName (buttonName)
                layout.addWidget (selectChatButton)
        else:
            label = QLabel ()
            label.setText ('No one has registered an account for you to chat with..')
            layout.addWidget (label)

        self.selectChatWidget.setLayout (layout)

    def chatWidgetUI (self):
        # This is the UI for the chatWidget.
        # Arrangement of the widgets
        layout = QVBoxLayout ()
        layoutTextInput = QGridLayout ()

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
        self.messageTextBox.returnPressed.connect (self.write)
        self.sendButton = QPushButton ()
        self.sendButton.setText ("Enter")
        self.sendButton.clicked.connect (self.write)

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
            self.awaitLoginEvent.wait (timeout=20)

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
        #chatText = "".join (self.chatHistory)
        self.chatBox.setText (self.chatHistory)

        # This keeps the scroll bar of the chatbox from riding up with new chats.
        self.chatScroll.verticalScrollBar ().setValue (self.chatScroll.verticalScrollBar ().maximum ())

    def selectChat (self):
        button = self.sender()
        buttonName = str (button.objectName())

        # Since the userId is appended onto the button with format
        # selectChatButton{userId}, we can parse the user id.
        self.chatRecipient = buttonName[16:]

        self.write ()

        # Place an event, waiting for the server to respond.
        self.awaitSelectChatEvent = threading.Event ()
        self.awaitSelectChatEvent.wait (timeout=5)

        # When the receiver thread has received the server's response...
        if self.awaitSelectChatEvent.isSet ():
            # If the event set, switch to the chat display and update the
            # chat history to include the past messages.
            self.chatWidgetUI ()
            self.display (3)
        else:
            print ("Timeout while waiting for server for dm information")
        print (f'Chatting with: {self.chatRecipient}')


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
                    for msg in message:
                        self.chatHistory += msg.getContents()[0]

                    self.awaitSelectChatEvent.set ()
                elif type == 'LoginConfirm':
                    # The server has confirmed that the user has a successful
                    # login.
                    self.username = self.usernameInput.text ()
                    self.allUserId = message

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
            # Messages to other user(s).
            if self.messageTextBox.text () != "":
                message = [f'{self.username}: {self.messageTextBox.text ()}\n']
                messageObj = pickle.dumps (Message ("Text", message))
                self.client.send (messageObj)

                # Sanitize.
                self.messageTextBox.clear ()
            else:
                # Choosing a user to chat with.
                if self.chatRecipient != "":
                    message = [self.chatRecipient]
                    messageObj = pickle.dumps (Message ('SwitchToDM', message))
                    self.client.send (messageObj)


    def start (self):
        # Thread starts and configurations.
        receive_thread = threading.Thread (target=self.receive)
        receive_thread.start ()

        write_thread = threading.Thread (target=self.write)
        write_thread.start ()