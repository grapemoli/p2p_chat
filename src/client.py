import socket
import threading
import pickle
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from message import Message


class Client (QMainWindow):
    username = ""
    client = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    client.connect (('50.90.134.19', 25565))

    def __init__ (self):
        super().__init__ ()

        # Set the window properties (title and initial size)
        self.setWindowTitle ("Chat Bocks")
        self.setGeometry (100, 100, 400, 300)  # (x, y, width, height)

        # Main window
        self.mainWindow = QWidget ()
        self.setCentralWidget (self.mainWindow)

        # Configure the current window to be scrollable, but we turn it on and
        # off based on the needs of the current displayed page.
        self.scroll = QScrollArea ()
        self.scroll.setHorizontalScrollBarPolicy (Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy (Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable (True)
        self.scroll.setWidget (self.mainWindow)
        self.setCentralWidget (self.scroll)

        # Initialize chat history, necessary widgets.
        self.messageTextBox = QLineEdit()
        self.chatHistory = []

        # Bring up the Chat Page
        self.loginPage ()


    # Pages / Widgets
    def loginPage (self):
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

        self.mainWindow.setLayout(layout)


    def chatPage (self):        # TODO: scroll bar, and achoring textbox
                                # TODO: clear textbox everytime you leave
        # Arrangement of the widgets
        layout = QGridLayout ()

        # Chatbox displays all sent and received messages.
        self.chatBox = QLabel ()
        self.chatBox.setWordWrap (True)  # Wrap long messages
        layout.addWidget (self.chatBox, 0, 0)

        # Text box area.
        #self.messageTextBox = QLineEdit ()
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
        self.mainWindow.setLayout (layout)


    def login (self):
        # Ask the server about this username-password pair.
        # If this is a legitimate account and credential, show the
        # chat screen.
        if (self.usernameInput.text () != "" and self.passwordInput.text () != ""):
            self.write ()

            if (self.username != ""):
                # Send the server the username.
                self.chatPage ()

        print (self.usernameInput.text ())  # TODO: remove, this is testing prints
        print (self.passwordInput.text ())


    def receive (self):
        while True:
            try:
                msgObject = pickle.loads (self.client.recv(1024))
                message = msgObject.getContents ()

                # Special (or normal) messages received from the server.
                if message == 'NameQuery':
                    # The implementation of this is that the server will keep asking
                    # for the username until the client's sent username is not an
                    # empty string. Username is ONLY set when there is a successful login.
                    self.client.send (self.username.encode ('ascii'))
                elif message == 'LoginConfirm':
                    # Successful login with this username!
                    self.username = self.usernameInput.text ()
                else:
                    # Normal message. Append to the chat history.
                    if (message != ""):
                        self.chatHistory.append (message)
                        self.update_chat_display ()
            except:
                print ("Error")
                self.client.close ()
                break


    def write (self):
        # While every textbox will be write to the server, not every
        # write will perform the same.

        # Not logged in.
        if self.username == "":

            # Only send a message if there are inputs for username and password.
            if self.usernameInput.text () != "" and self.passwordInput.text () != "":
                message = f'{self.usernameInput.text ()},{self.passwordInput.text ()}'
                messageToSend = pickle.dumps (Message("LoginReq", message))
                self.client.send (messageToSend)

        # Logged in.
        elif self.username != "":

            # Only send a message if there is content in the textbox.
            if self.messageTextBox.text() != "":
                message = f'{self.username}: {self.messageTextBox.text ()}'
                messageToSend = pickle.dumps (Message ("None", message))
                self.client.send (messageToSend)

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
