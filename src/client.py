import socket
import threading


class Client:
    username = ""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect (('50.90.134.19', 25565))

    def __init__ (self):
        self.username = input ('What is your username? ')

    def receive (self):
        while True:
            try:
                message = self.client.recv (1024).decode ('ascii')
                if message == 'NAME_QUERY':
                    self.client.send (self.username.encode ('ascii'))
                else:
                    print(message)
            except:
                print ("Error")
                self.client.close
                break

    def write (self):
        while True:
            message = f'{self.username}: {input ("")}'
            self.client.send (message.encode ('ascii'))

    def start (self):
        receive_thread = threading.Thread (target=self.receive)
        receive_thread.start ()

        write_thread = threading.Thread (target=self.write)
        write_thread.start ()