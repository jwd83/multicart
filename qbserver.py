import socket
import pickle
import threading
import scenes.quadblox.scripts.qb
import configparser

class QBServer:
    def __init__(self):
        print("Initializing QuadBlox server...")
        # maintain a list of clients
        self.clients = []
        self.aliases = []

        # setup our default values
        self.host : str = 'localhost' # default host
        self.port : int = 64209 # meme number default port in the iana private port range (49152–65535)

        # load the config file
        self.config = configparser.ConfigParser()
        self.config.read("assets/config.ini")
        # check if the main section exists
        if "main" in self.config:
            # check if the fullscreen setting exists
            if "host" in self.config["main"]:
                self.host : str = self.config["main"].get("host")
                print(f"config.ini:main.host: {self.host}")
            if "port" in self.config["main"]:
                self.port : int = self.config["main"].getint("port")
                print(f"config.ini:main.port: {self.port}")

        self.sock : socket.socket | None = None


    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024)
                self.broadcast(message)
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                alias = self.aliases[index]
                self.broadcast(f'{alias} has left the chat room!'.encode('utf-8'))
                self.aliases.remove(alias)
                break

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    def run(self):

        print(f"Starting QuadBlox server on {self.host}:{self.port}")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind config is a tuple of host and port... weird python syntax
        self.sock.bind((self.host, self.port))

        # start list for connections
        self.sock.listen()

        while True:
            print('Awaiting connection...')
            client, address = self.sock.accept()
            client.send('alias?'.encode('utf-8'))
            alias = client.recv(1024)
            self.aliases.append(alias)
            self.clients.append(client)
            print(f'{str(address)} connected as {alias}'.encode('utf-8'))
            self.broadcast(f'<{alias}> connected'.encode('utf-8'))
            client.send('Connected to server'.encode('utf-8'))
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()

def main():

    q = QBServer()
    q.run()

if __name__ == '__main__':
    main()
