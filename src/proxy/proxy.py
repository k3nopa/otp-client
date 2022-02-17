from threading import Thread
import socket
import binascii
import traceback
import os
import onetimepad
import otp
import helpers


class Proxy(Thread):
    def __init__(self, client, server, port, stopEvent, otp=False, layer=128, height=7):
        Thread.__init__(self)

        self.client = client
        self.server = server
        self.port = port
        self.stopEvent = stopEvent
        self.select = helpers.Select()
        self.otp = otp
        self.key = ""
        self.layer = layer
        self.height = height

        self.tree = {}  # hold every IoT's past connection's OTP information.
        self.session_count = 0
        self.connection = {}    # Hold current active connections.
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

                    helpers.logger("info", f"Connection from {client_addr}")

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

                    if self.otp:    # Decrypt (Receive Data).
                        if readSock.fileno() > writeFd:
                            data = readSock.recv(1024)  # Packet from Broker
                        else:
                            try:
                                ip_addr = readSock.getpeername()[0]
                                if self.tree.get(ip_addr) == None:
                                    helpers.logger("info", "Starting Diffie-Hellman Exhange")

                                    ecdh_key = helpers.init_diffie_hellman(readSock)

                                    helpers.logger("info", f"ECDH Key = {ecdh_key}")
                                    helpers.logger("info", "Fetching OTP Tree.")

                                    data = otp.fetch_tree(
                                        sock=readSock,
                                        dec_key=self.key.hex(),
                                        layer=self.layer,
                                    )
                                    self.tree[ip_addr] = data

                                    helpers.logger("info", "Done fetching OTP Tree.")

                                else:
                                    if not self.in_session:
                                        helpers.logger("info", "Creating New Session.")
                                        path, layer = otp.fetch_path(readSock)

                                        otp_key = otp.fetch_key(
                                            tree=self.tree[ip_addr],
                                            path=int(path),
                                            layer=layer,
                                            height=self.height,
                                        )

                                        self.key = str(otp_key)
                                        self.in_session = True
                                        self.session_count += 1

                                    data = readSock.recv(1024)
                                    dec_data = onetimepad.decrypt(data.hex(), self.key)
                                    try:
                                        data = binascii.unhexlify(dec_data)
                                        helpers.logger(f"H: {self.height}, L: {self.layer}", f"Session {self.session_count} => Key: {self.key}, Len Data Recv: {len(data)}", "info")
                                    except Exception:
                                        helpers.logger(f"H: {self.height}, L: {self.layer}", f"Session {self.session_count} => Key: {self.key}, Decoding Error.", "warn")

                            except Exception as e:
                                helpers.logger("error", f"Client Decryption Error\n{e}")
                                os.sys.exit()
                    else:
                        data = readSock.recv(1024)

                    if not data:
                        del self.connection[fd]
                        self.select.removeConnection(readSock)
                        readSock.close()

                        del self.connection[writeFd]
                        self.select.removeConnection(writeSock)
                        writeSock.close()
                        self.in_session = False

                        helpers.logger("info", f"Client Disconnected ({fd}) <-> ({writeFd})")
                    
                    if self.otp:   # Encrypt (Send Data). 
                        # If packet came from client, send to broker without encrypting it.
                        if readSock.fileno() < writeFd and writeSock.fileno() > 0 and type(data) == bytes:
                            writeSock.sendall(data)
                        elif writeSock.fileno() > 0 and type(data) == bytes:
                            helpers.send_mqtt_packet(writeSock, self.key, data)

                    elif writeSock.fileno() > 0 and type(data) == bytes:
                        writeSock.sendall(data)

        # Clean up all connections.
        for connection in self.connection:
            sock, fd = connection
            sock.close()
        self.socket.close()