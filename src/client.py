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

        # Set the window properties (title and initial size)
        self.setWindowTitle ("ChatBocks Login")
        self.setGeometry (100, 100, 400, 300)  # (x, y, width, height)

        # Main window: holds the stack of other layouts to provide a single-page
        # application that hosts multiple UIs (as opposed to opening a lot of new
        # windows for each UI).
        self.mainWindow = QWidget ()
        self.stack = QStackedLayout ()
        self.mainWindow.setLayout (self.stack)


        # Create the other UI's and put them in a list to keep track of them. This
        # list is also what we use to switch between the UI's.
        self.loginWidget = QWidget ()
        self.addAccountWidget = QWidget ()
        self.chatWidget = QWidget ()

        self.setupUI ()

        self.stack.addWidget (self.loginWidget)
        self.stack.addWidget (self.addAccountWidget)
        self.stack.addWidget (self.chatWidget)

        # Configure the current window to be scrollable. We can turn it on and
        # off based on the needs of the current displayed page. For now, only
        # enable vertical scrolling.
        self.scroll = QScrollArea ()
        self.scroll.setHorizontalScrollBarPolicy (Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy (Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable (True)
        self.scroll.setWidget (self.mainWindow)
        self.setCentralWidget (self.scroll)

        # Initialize chat history for the chatting function.
        self.chatHistory = []

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
        self.newUsernameInput.clear()
        self.newPasswordInput.clear()
        self.usernameInput.clear()
        self.passwordInput.clear()

        # Change the window title based on the UI we switch to.
        if index == 0:
            self.setWindowTitle ('ChatBox Login')
        if index == 1:
            self.setWindowTitle ('Create an Account')
        if index == 2:
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
        self.chatWidgetUI ()

    def loginWidgetUI (self):
        # This is the UI for the login widget initialized in the initializer.
        # TODO: add validation msgs (textbox with error from server)
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

        self.addAccountWidget.setLayout (layout)

    def chatWidgetUI (self):
        # This is the UI for the chatWidget.
        # Arrangement of the widgets
        layout = QGridLayout ()

        # Chatbox displays all sent and received messages.
        self.chatBox = QLabel ()
        self.chatBox.setWordWrap (True)  # Wrap long messages
        layout.addWidget (self.chatBox, 0, 0)

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
        layout.addWidget (self.messageTextBox, 1, 0)
        layout.addWidget (self.sendButton, 1, 1)

        # Set the layout for the central widget
        self.chatWidget.setLayout (layout)


    ####################################
    # Event Handlers
    ####################################
    def login (self):
        # Send a request to the server about the username and password inputted.
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
                self.display (2)

    def addAccount(self):
        # Send a request to the server about the username and password inputted.
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

    def updateChatDisplay (self):
        # This is for live chat updates.
        chatText = "\n".join (self.chatHistory)
        self.chatBox.setText (chatText)


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
                if type == 'LoginConfirm':
                    # The server has confirmed that the user has a successful
                    # login.
                    self.username = self.usernameInput.text ()

                    # Release the client's wait on the server to reply.
                    self.awaitLoginEvent.set ()
                elif type == 'LoginFailure':
                    self.awaitLoginEvent.set()
                elif type == 'CreateConfirm':
                    # Successful creation!
                    self.username = self.newUsernameInput.text ()
                    self.awaitAddUserEvent.set ()
                elif type == 'CreateFailure':
                    self.awaitAddUserEvent.set()
                else:
                    # Normal message. Append to the chat history.
                    if (message != ""):
                        self.chatHistory.append (message)
                        self.updateChatDisplay ()
            except Exception as e:
                # Any failure will forcibly close the connection.
                print (e)
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
                message = f'{self.usernameInput.text ()},{self.passwordInput.text ()}'
                loginObj = pickle.dumps (Message ("LoginReq", message))
                self.client.send (loginObj)

            # Account Creation: is the account the user is trying to make valid?
            elif self.newUsernameInput.text() != "" and self.newPasswordInput.text () != "":
                message = f'{self.newUsernameInput.text ()},{self.newPasswordInput.text ()}'
                createObj = pickle.dumps (Message ("CreateAccount", message))
                self.client.send (createObj)

        # The client can only send these type of messages to the server if the user is logged in.
        # This acts as a privilege scoping.
        elif self.username != "":

            # Messages to other user(s).
            if self.messageTextBox.text () != "":
                message = f'{self.username}: {self.messageTextBox.text ()}'
                messageObj = pickle.dumps (Message ('Message', message))
                self.client.send (messageObj)

                # Manipulate the UI to show the sent message in the chatbox. Then
                # clear the textbox.
                self.updateChatDisplay ()
                self.messageTextBox.clear ()

    def start (self):
        # Thread starts and configurations.
        receive_thread = threading.Thread (target=self.receive)
        receive_thread.start ()

        write_thread = threading.Thread (target=self.write)
        write_thread.start ()