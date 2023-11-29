class Message(object):
    def __init__(self, type, contents):
        #initialize members
        self.type_ = type
        self.contents_ = contents

    def getType(self):
        return self.type_
    
    def getContents(self):
        return self.contents_