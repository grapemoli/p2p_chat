########################################################################
# Types of Messages:
#
#
# ACK - successful connection between the server and client
#
#
# LoginReq - requests server to see if credentials are correct
#          - content: '{username},{password}'
# LoginConfirm - response from server that credentials are valid
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
# "" - ...or no type; a message sent from a user to another user
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