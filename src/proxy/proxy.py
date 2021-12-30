from threading import Thread
import socket
import binascii
import traceback
import os

import onetimepad
import ecdh
import otp
import helpers

LAYER = 30
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

        # NOTE: hold every IoT's past connection's OTP information.
        self.tree = {}
        # Hold current active connections.
        self.connection = {}
        self.in_session = False

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
                # If selected socket is open & is a server.
                if fd == self.socket.fileno():

                    client_s, client_addr = self.socket.accept()
                    server_s = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM)
                    server_s.connect((self.client, self.port))

                    clientFd = client_s.fileno()
                    serverFd = server_s.fileno()

                    self.select.addConnection(client_s)
                    self.select.addConnection(server_s)

                    self.connection[clientFd] = (client_s, serverFd)
                    self.connection[serverFd] = (server_s, clientFd)

                    print(f"Connection from {client_addr}")

                else:
                    # If a socket is already connected.
                    if fd in self.connection:
                        readSock, writeFd = self.connection[fd]
                    else:
                        continue

                    if writeFd in self.connection:
                        # If a sending to socket is already connected.
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
                                ip_addr = readSock.getpeername()[0]
                                if self.tree.get(ip_addr) == None:
                                    print("Starting Diffie-Hellman Exhange")

                                    ec = ecdh.ECDH(readSock)
                                    peer_pub = ec.recv_pub_key()
                                    ec.send_pub_key(ec.export_key())
                                    peer_pub_key = ec.import_key(peer_pub)
                                    self.key = ec.shared_key(peer_pub_key)

                                    print("Receiving OTP Tree.")
                                    data = otp.fetch_tree(
                                        sock=readSock, dec_key=self.key.hex(), layer=LAYER
                                    )
                                    self.tree[ip_addr] = data
                                    print("Finished receiving OTP Tree.")

                                else:
                                    if not self.in_session:
                                        # Fetch new path.
                                        print("Fetch path.")
                                        path, layer = otp.fetch_path(readSock)
                                        print(f"Path: {path}, Layer: {layer}")
                                        self.in_session = True

                                        otp_key = otp.fetch_key(
                                            tree=self.tree[ip_addr], path=int(path), layer=layer, height=HEIGHT
                                        )

                                        self.key = str(otp_key)
                                        # print("Key: ", self.key)

                                    data = readSock.recv(1024)
                                    dec_data = onetimepad.decrypt(
                                        data.hex(), self.key)
                                    try:
                                        data = binascii.unhexlify(dec_data)
                                        # print("[RECV] ", data)
                                    except Exception as e:
                                        print("Unhexlify Error ", dec_data)

                            except Exception as e:
                                print("Client Decryption problem ",
                                      traceback.format_exc())
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
                        self.in_session = False

                        print(f"Disconnected - ({fd}) <-> ({writeFd}).")

                    # Encrypt (Send Data).
                    if self.otp:
                        # If packet came from client, send to server without encrypting it.
                        if readSock.fileno() < writeFd:
                            if writeSock.fileno() > 0 and type(data) == bytes:
                                # print("[SEND BROKER] ", data)
                                writeSock.sendall(data)
                        else:

                            if writeSock.fileno() > 0 and type(data) == bytes:
                                # print("[SEND CLIENT] ", data)
                                # Send first byte fixed header
                                byte_data = onetimepad.encrypt(
                                    data[:1].hex(), self.key)
                                writeSock.sendall(
                                    binascii.unhexlify(byte_data))

                                # Send second byte fixed header
                                byte_data = onetimepad.encrypt(
                                    data[1:2].hex(), self.key)
                                writeSock.sendall(
                                    binascii.unhexlify(byte_data))

                                # Send remaining
                                byte_data = onetimepad.encrypt(
                                    data[2:].hex(), self.key)
                                writeSock.sendall(
                                    binascii.unhexlify(byte_data))
                    else:
                        if writeSock.fileno() > 0 and type(data) == bytes:
                            writeSock.sendall(data)

        # Clean up all connections.
        for connection in self.connection:
            sock, fd = connection
            sock.close()
        self.socket.close()
