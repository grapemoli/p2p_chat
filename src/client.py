import socket
import threading
import pickle
import sys
from PyQt6.QtWidgets import *


class Client (QMainWindow):
    username = "grace"                                    # TODO: configure this on the login screen
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('50.90.134.19', 25565))

    def __init__ (self):
        #self.username = input ('What is your username? ')  # TODO: make this the first thing that appears
        super().__init__ ()

        # Set the window properties (title and initial size)
        self.setWindowTitle ("Chat Bocks")
        self.setGeometry (100, 100, 400, 300)  # (x, y, width, height)

        # Main window
        mainWindow = QWidget ()
        self.setCentralWidget (mainWindow)

        # Arrangement of the widgets
        layout = QGridLayout ()

        # Displaying live messages
        self.chatBox = QLabel ()
        self.chatBox.setWordWrap (True)  # Wrap long messages
        layout.addWidget (self.chatBox)

        # Inline: text box, enter button
        messageLayout = QGridLayout ()
        self.messageTextBox = QLineEdit ()
        self.messageTextBox.font ().setPointSize(18)
        self.messageTextBox.setPlaceholderText ("Type your message...")
        self.messageTextBox.returnPressed.connect (self.write)
        self.sendButton = QPushButton ()
        self.sendButton.setText ("Enter")       # TODO: use grid properties to align in a line
        #self.sendButton.clicked.connect (self.write)
        #messageLayout.addWidget (self.messageTextBox, 0, 0, 0, 0)
        #messageLayout.addWidget (self.sendButton, 0, 0, 0, 1)
        layout.addWidget (self.messageTextBox)
        layout.addWidget (self.sendButton)
        #layout.addWidget (messageLayout)

        # Set the layout for the central widget
        mainWindow.setLayout (layout)

        # Initialize chat history
        self.chatHistory = []

    def receive (self):
        while True:
            try:
                message = self.client.recv (1024).decode ('ascii')
                if message == 'NAME_QUERY':
                    self.client.send (self.username.encode ('ascii'))
                else:
                    # Append to the chat history
                    if (message != ""):
                        self.chatHistory.append (message)
                        self.update_chat_display ()
            except:
                print ("Error")
                self.client.close ()
                break

    def write (self):
        if self.messageTextBox.text() != "":
            message = f'{self.username}: {self.messageTextBox.text ()}'
            toSend = pickle.dumps(Message("", message))
            self.client.send (toSend)
            self.update_chat_display ()
            self.messageTextBox.clear ()

    def update_chat_display (self):
        # Display the chat history in the QLabel
        chat_text = "\n".join (self.chatHistory)
        self.chatBox.setText (chat_text)

    def start (self):
        receive_thread = threading.Thread (target=self.receive)
        receive_thread.start ()

        write_thread = threading.Thread (target=self.write)
        write_thread.start ()

class Message(object):
    def __init__(self, type, contents):
        #initialize members
        self.type_ = type
        self.contents_ = contents

    def getType(self):
        return self.type_
    
    def getContents(self):
        return self.contents_