import select
from socket import SocketIO
import ecdh
import onetimepad
import binascii

class Colors:
    INFO = "\033[96m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    END = "\033[0m"


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
                yield connection.fileno()


def logger(status: str, msg: str, override: str = ""):
    if override == "":
        output = status.capitalize()
    else: 
        output = override

    if status == "error":
        print(f"{Colors.ERROR}[{output}]{Colors.END} {msg}")
    elif status == "warn":
        print(f"{Colors.WARNING}[{output}]{Colors.END} {msg}")
    else:   # info
        print(f"{Colors.INFO}[{output}]{Colors.END} {msg}")

def init_diffie_hellman(sock: SocketIO):
    ec = ecdh.ECDH(sock)
    peer_pub = ec.recv_pub_key()
    ec.send_pub_key(ec.export_key())
    peer_pub_key = ec.import_key(peer_pub)
    return ec.shared_key(peer_pub_key)

def send_mqtt_packet(sock: SocketIO, key: str, data: bytes):
    # Send first byte fixed header
    byte_data = onetimepad.encrypt(data[:1].hex(), key)
    sock.sendall(binascii.unhexlify(byte_data))

    # Send second byte fixed header
    byte_data = onetimepad.encrypt(data[1:2].hex(), key)
    sock.sendall(binascii.unhexlify(byte_data))

    # Send remaining
    byte_data = onetimepad.encrypt(data[2:].hex(), key)
    sock.sendall(binascii.unhexlify(byte_data))