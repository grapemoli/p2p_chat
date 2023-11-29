class Message (object):
    def __init__ (self, type, contents):
        # Initialize members.
        self.type_ = type
        self.contents_ = contents

    # Existing Types:
    # ACK - successful connection
    # LoginReq
    # LoginConfirm
    # LoginFailure
    # CreateConfirm
    # "" - default, a message sent by a user
    def getType (self):
        return self.type_
    
    def getContents (self):
        return self.contents_