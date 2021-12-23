import select
import onetimepad
import binascii


class Select:
    def __init__(self):

        self.readList = []
        # Hold the selected socket.
        self.readable = None

    def addConnection(self, connection):
        self.readList.append(connection)

    def removeConnection(self, connection):
        self.readList.remove(connection)

    def wait(self, timeout):
        try:
            # Return socket that had been selected.
            self.readable, _, _ = select.select(self.readList, [], [], timeout)
            return True
        except select.error as e:
            return False

    def loop(self):
        if self.readable is not None:
            for connection in self.readable:
                # Pass current running process to run another code with return value.
                yield connection.fileno()


def broker2client(writeSock, data, key):
 # Send first byte fixed header
    byte_data = onetimepad.encrypt(
        data[:1].hex(), key)
    writeSock.sendall(binascii.unhexlify(byte_data))

    # Send second byte fixed header
    byte_data = onetimepad.encrypt(
        data[1:2].hex(), key)
    writeSock.sendall(binascii.unhexlify(byte_data))

    # Send remaining
    byte_data = onetimepad.encrypt(
        data[2:].hex(), key)
    writeSock.sendall(binascii.unhexlify(byte_data))
    pass


def client2broker():
    pass
