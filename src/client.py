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

    def __init__ (self):
        super().__init__ ()

        # Set the window properties (title and initial size)
        self.setWindowTitle ("Chat Bocks")
        self.setGeometry (100, 100, 400, 300)  # (x, y, width, height)

        # Main window
        self.mainWindow = QWidget ()        # mainWindow holds switchWindow, who holds windowList and the stack of other windows
        self.setCentralWidget(self.mainWindow)

        self.stack = QStackedLayout ()


        # Create other windows & put them in the list to keep track of them.
        self.loginWidget = QWidget ()
        self.addAccountWidget = QWidget ()
        self.chatWidget = QWidget ()

        self.setupUI ()

        self.stack.addWidget (self.loginWidget)
        self.stack.addWidget (self.addAccountWidget)
        self.stack.addWidget (self.chatWidget)

        # Configure the current window to be scrollable, but we turn it on and
        # off based on the needs of the current displayed page.
        self.scroll = QScrollArea ()
        self.scroll.setHorizontalScrollBarPolicy (Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy (Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable (True)
        self.scroll.setWidget (self.mainWindow)
        self.setCentralWidget (self.scroll)

        # Initialize chat history, necessary widgets.
        self.chatHistory = []

        # Begin the display at the login page.
        self.configureButtons ()
        self.display (0)


    # Pages / Widgets
    def display (self, index):
        # For switching between different windows with only one window.
        self.stack.setCurrentIndex (index)
        self.newUsernameInput.clear()
        self.newPasswordInput.clear()
        self.usernameInput.clear()
        self.passwordInput.clear()

    def setupUI (self):
        self.loginWidgetUI ()
        self.addAccountWidgetUI ()
        self.chatWidgetUI ()

    def configureButtons (self):
        # Configures all the buttons that will "change the windows." The configuration is
        # done here because the UI needs to be loaded before it can reference another UI; however,
        # the login and add account windows have buttons that point to each other--a circular need.
        # So, we make the window-changing buttons in their respective UI methods, but configure here.
        self.toAddAccountButton.clicked.connect (lambda: self.display(1))
        self.toAddAccountButton.clicked.connect (lambda: self.newUsernameInput.setText(''))
        self.toAddAccountButton.clicked.connect (lambda: self.newPasswordInput.setText(''))
        self.toLoginButton.clicked.connect (lambda: self.display(0))
        self.toLoginButton.clicked.connect (lambda: self.usernameInput.clear())
        self.toLoginButton.clicked.connect (lambda: self.passwordInput.clear())

    def loginWidgetUI (self):
        # TODO: add validation msgs (textbox with error from server)
        # TODO: login enter button

        # Login form label.
        layout = QGridLayout()

        # Username input.
        usernameLabel = QLabel ('<font size="4"> Username </font>')
        self.usernameInput = QLineEdit()
        self.usernameInput.setPlaceholderText ('Please enter your username')
        layout.addWidget (usernameLabel, 0, 0)
        layout.addWidget (self.usernameInput, 0, 1)

        # Password input.
        passwordLabel = QLabel ('<font size="4"> Password </font>')
        self.passwordInput = QLineEdit ()
        self.passwordInput.setPlaceholderText( 'Please enter your password')
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
        self.toAddAccountButton.setText ('To Add Account')
        layout.addWidget (self.toAddAccountButton)

        self.loginWidget.setLayout (layout)

    def addAccountWidgetUI (self):
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
        
        addAccountButton = QPushButton ('Add this Account')
        addAccountButton.clicked.connect (self.addAccount)
        layout.addWidget (addAccountButton, 2, 0, 1, 2)
        layout.setRowMinimumHeight (2, 75)

        # Button to create login page.
        self.toLoginButton = QPushButton ()
        self.toLoginButton.setText ('Go To Login')
        layout.addWidget (self.toLoginButton)

        self.addAccountWidget.setLayout (layout)

    def chatWidgetUI (self):        # TODO: scroll bar, and achoring textbox
                                # TODO: clear textbox everytime you leave
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


    # Actions for Widgets / Event Handlers.
    def addAccount (self):
        # Does not validate the username or password.
        self.write ()

    def login (self):
        # Ask the server about this username-password pair.
        # If this is a legitimate account and credential, show the
        # chat screen.
        self.write ()

        if (self.username != ""):
            # Send the server the username.
            self.display (2)


    # Message Methods.
    def receive (self):
        while True:
            try:
                msgObject = pickle.loads (self.client.recv (1024))
                type = msgObject.getType ()
                message = msgObject.getContents ()

                # Special (or normal) messages received from the server.
                if type == 'LoginConfirm':
                    # Successful login with this username!
                    self.username = self.usernameInput.text ()
                elif type == 'LoginFailure':
                    pass
                elif type == 'CreateConfirm':
                    # Successful creation!
                    self.username = self.newUsernameInput.text ()

                else:
                    # Normal message. Append to the chat history.
                    if (message != ""):
                        self.chatHistory.append (message)
                        self.update_chat_display ()
            except Exception as e:
                print (e)
                self.client.close ()
                break


    def write (self):
        # While every textbox will be a write to the server, not every
        # write will perform the same way.

        # Not logged in.
        if self.username == "":
            # Only send a request to the server if there are inputs for username and password.

            if self.usernameInput.text () != "" and self.passwordInput.text () != "":

                # Login
                message = f'{self.usernameInput.text ()},{self.passwordInput.text ()}'
                loginObj = pickle.dumps (Message ("LoginReq", message))
                self.client.send (loginObj)

            elif self.newUsernameInput.text() != "" and self.newPasswordInput.text () != "":

                # Account Creation
                message = f'{self.newUsernameInput.text ()},{self.newPasswordInput.text ()}'
                createObj = pickle.dumps(Message("CreateAccount", message))
                self.client.send (createObj)

        # Logged in.
        elif self.username != "":

            # Only send a message if there is content in the textbox.
            if self.messageTextBox.text() != "":
                message = f'{self.username}: {self.messageTextBox.text ()}'
                messageObj = pickle.dumps (Message ("", message))
                self.client.send (messageObj)

                # Manipulate the display to show the sent message, and clear the
                # textbox.
                self.update_chat_display ()
                self.messageTextBox.clear ()

    def update_chat_display (self):
        chat_text = "\n".join (self.chatHistory)
        self.chatBox.setText (chat_text)

    def start (self):
        receive_thread = threading.Thread (target=self.receive)
        receive_thread.start ()

        write_thread = threading.Thread (target=self.write)
        write_thread.start ()
