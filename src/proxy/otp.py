import socket
import onetimepad
import json
from binarytree import build, Node
from enum import Enum, auto


class Status(Enum):
    R_SIZE = auto()
    R_DATA = auto()
    COMPLETE = auto()


def fetch_tree(sock: socket.SocketIO, dec_key, layer: int) -> None:
    """
    Handles the fetching process of OTP's information from client side.
    """
    # 1. Fetch the data (the key memory cell with it's id)
    tree = []
    packet = ""
    status = Status.R_SIZE
    count = 0
    while True:

        if status == Status.R_SIZE:
            # Size was sent without any encryption.
            size = sock.recv(10)
            status = Status.R_DATA

        if status == Status.R_DATA:
            size = int(size)
            while size > 0:
                data = sock.recv(4096)
                size -= len(data)
                packet += data.decode()

            status = Status.COMPLETE

        if status == Status.COMPLETE:
            dec_data = onetimepad.decrypt(packet, dec_key)
            l = json.loads(dec_data)
            tree.append(l)
            count += 1
            packet = ""
            status = Status.R_SIZE

        if not size and count == layer:
            return tree


def fetch_path(sock: socket.SocketIO):
    """
    Handles fetching path and parsing it from the client side.
    Returns a tuple of path:str & layer:int
    """
    packet = ""
    count = 0
    data = []
    status = Status.R_SIZE
    while True:

        if status == Status.R_SIZE:
            # Size was sent without any encryption.
            size = sock.recv(10)
            status = Status.R_DATA
            print("Reading size of ", size)

        if status == Status.R_DATA:
            size = int(size)
            while size > 0:
                read_byte = sock.recv(100)
                size -= len(read_byte)
                packet += read_byte.decode()

            status = Status.COMPLETE

        if status == Status.COMPLETE:
            print("Parsing complete packet ", packet)
            data.append(int(packet))
            count += 1
            packet = ""
            status = Status.R_SIZE

        if not size and count == 2:
            return (data[0], data[1])


def fetch_key(tree, path: int, layer: int, height: int) -> str:
    """
    From given tree array containing only the keys, first we generate the necessary decision tree from given layer.
    Then, we traverse generated OTP decision tree using the given path to obtain the key.
    """

    # 1. Generate the necessary tree.
    decision_tree = []
    # 1-1. Generate all switches nodes.
    decision_tree.append(-1)
    for i in range(1, height):
        total_switch = 2**i
        while total_switch > 0:
            decision_tree.append(-1)
            total_switch -= 1

    # 1-2. Add all key memory nodes from succcess layer.
    key_nodes = tree[layer]
    assert len(key_nodes) == (2**height), "Key Nodes aren't complete."
    for key in key_nodes:
        decision_tree.append(key)

    # 1-3. Build the tree.
    root = build(decision_tree)

    # 2. Traverse the tree using the path:int.
    path_bin = bin(path)[2:]
    # Make sure len of path is appropriate.
    path_bin = path_bin[(len(path_bin) - height):]
    key = __get_key(path_bin, root)
    return key


def __get_key(path_bin: str, node: Node) -> int:
    if node.value != -1:
        # Managed to reach memory node.
        return node.value

    for c in path_bin:
        if c == '0':
            return __get_key(path_bin[1:], node.left)
        else:
            return __get_key(path_bin[1:], node.right)
