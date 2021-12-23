from threading import Thread
import socket
import select
import binascii

import onetimepad
import parser
import ecdh
import otp

import os

import helpers
LAYER = 10
HEIGHT = 7


class Proxy(Thread):
    def __init__(self, client, server, port, stopEvent, otp=False):
        Thread.__init__(self)

        self.client = client
        self.server = server
        self.port = port
        self.stopEvent = stopEvent
        self.select = helpers.Select()
        self.otp = otp
        self.key = ""
        # TODO: hold every IoT's past connection's OTP information.
        # TODO: Store Address(key) to OTP class (value).
        self.tree = {}

        # Hold current active connections.
        self.connection = {}

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.socket.bind((self.client, port))
            self.socket.listen(5)

            self.select.addConnection(self.socket)

        except socket.gaierror as e:
            raise e

    def run(self):
        self.err = 0

        # While not Ctrl-C
        while not self.stopEvent.is_set():
            # Start selection step.
            if not self.select.wait(0.05):
                self.err = 1
                break

            for fd in self.select.loop():
                # If a socket is open.
                # If selected socket is server.
                if fd == self.socket.fileno():

                    client_s, client_addr = self.socket.accept()
                    clientFd = client_s.fileno()

                    server_s = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM)
                    server_s.connect((self.client, self.port))
                    serverFd = server_s.fileno()

                    self.select.addConnection(client_s)
                    self.connection[clientFd] = (client_s, serverFd)

                    self.select.addConnection(server_s)
                    self.connection[serverFd] = (server_s, clientFd)

                    print(f"Connection from {client_addr}")

                # If a socket is already connected.
                else:
                    if fd in self.connection:
                        readSock, writeFd = self.connection[fd]
                    else:
                        continue

                    # If a sending to socket is already connected.
                    if writeFd in self.connection:
                        writeSock, _ = self.connection[writeFd]
                    else:
                        continue

                    # Decrypt (Receive Data).
                    if self.otp:

                        if readSock.fileno() > writeFd:
                            # Packet from Broker
                            data = readSock.recv(1024)
                        else:
                            # Packet from Client
                            try:
                                ip_addr, _ = readSock.getpeername()
                                if self.tree.get(ip_addr) == None:
                                    print("Starting Diffie-Hellman Exhange")
                                    ec = ecdh.ECDH(readSock)
                                    # 1. Recv A
                                    peer_pub = ec.recv_pub_key()
                                    # 2. Send B
                                    ec.send_pub_key(ec.export_key())
                                    # 3. Generate Shared Key
                                    peer_pub_key = ec.import_key(peer_pub)
                                    self.key = ec.shared_key(peer_pub_key)
                                    print("Share Key: ", self.key)

                                    # NOTE: Data already encrypted.
                                    print("Receiving OTP Tree.")
                                    tree = otp.fetch_tree(
                                        sock=readSock, dec_key=self.key.hex(), layer=LAYER
                                    )
                                    self.tree[ip_addr] = tree
                                    print("Finished receiving OTP Tree.")
                                    data = b''
                                else:
                                    print("Trying to fetch path.")

                                    path, layer = otp.fetch_path(readSock)
                                    print(f"Path: {path}, Layer: {layer}")

                                    otp_key = otp.fetch_key(
                                        tree=self.tree[ip_addr], path=int(path), layer=layer, height=HEIGHT
                                    )

                                    print("Key: ", otp_key)
                                    print("MQTT Handling")

                                    # MQTT Packet Handling
                                    data = readSock.recv(1024)
                                    data = onetimepad.decrypt(
                                        data.hex(), self.key)
                                    data = binascii.unhexlify(data)

                            except Exception as e:
                                print("Client Decryption problem ", e)
                                os.sys.exit()
                    else:
                        data = readSock.recv(1024)

                    if not data:
                        # If no longer receiving data close socket.
                        del self.connection[fd]
                        self.select.removeConnection(readSock)
                        readSock.close()

                        del self.connection[writeFd]
                        self.select.removeConnection(writeSock)
                        writeSock.close()

                        print(f"Disconnected - ({fd}) <-> ({writeFd}).")
                        continue
                    # TODO: Fixed parser to able to use for non otp connections.
                    # packet_type, content = parser.parser(data)
                    # print(f"[{packet_type}] {content}")

                    # Encrypt (Send Data).
                    if self.otp and self.tree.get(ip_addr) != None:
                        # If packet came from client, send to server without encrypting it.
                        if readSock.fileno() < writeFd:
                            writeSock.sendall(data)
                        else:
                            # Send first byte fixed header
                            byte_data = onetimepad.encrypt(
                                data[:1].hex(), self.key)
                            writeSock.sendall(binascii.unhexlify(byte_data))

                            # Send second byte fixed header
                            byte_data = onetimepad.encrypt(
                                data[1:2].hex(), self.key)
                            writeSock.sendall(binascii.unhexlify(byte_data))

                            # Send remaining
                            byte_data = onetimepad.encrypt(
                                data[2:].hex(), self.key)
                            writeSock.sendall(binascii.unhexlify(byte_data))
                    else:
                        writeSock.sendall(data)

        # Clean up all connections.
        for connection in self.connection:
            sock, fd = connection
            sock.close()
        self.socket.close()
