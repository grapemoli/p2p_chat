########################################################################
# Types of Messages:            (content is a list)
#
#
# ACK - successful connection between the server and client
#
#
# LoginReq - requests server to see if credentials are correct
#          - content: '{username},{password}'
# LoginConfirm - response from server that credentials are valid
#              - content: {[userId, username],{userId2, username2},...}
# LoginFailure - response from server that credentials are invalid
#              - content: gives details on why the login failed
#
#
# CreateAccount - requests server if account was successfully made with params
#               - content: '{username},{password}'
# CreateConfirm - positive response from server
# CreateFailure - negative response from server
#
#
# "Text" - a message sent from a user to another user
#    - content: '{username}: {message}'
#
#
# SwitchToDM - tells the server that the user to chat with
#            - content: '{userId of chat recipient}'
# DMConfirm - tells the client that chatroom is successfully established!
#           - content: {list of messages}
# CloseDM - [from client] tells the server that the user has left the chat
#         - [from client] content: {}
#         - [from server] tells the client the close DM was received, and sends an updated user list
#         - [from server] content: {userId, ..., }          <-- exclusive of the client's userId
########################################################################

class Message (object):
    ####################################
    # Initialize
    ####################################
    def __init__ (self, type, contents):
        # Initialize members.
        self.type_ = type
        self.contents_ = contents


    ####################################
    # Methods
    ####################################
    def getType (self):
        return self.type_
    
    def getContents (self):
        return self.contents_