import socket
from typing import List
import onetimepad
import json
from binarytree import build, Node
from enum import Enum, auto


class __Status(Enum):
    SIZE = auto()
    DATA = auto()
    COMPLETE = auto()


def fetch_tree(sock: socket.SocketIO, dec_key, layer: int) -> None:
    """
    Fetching whole OTP decision tree information from client side.
    """
    # 1. Fetch the data (the key memory cell with it's id)
    tree = []
    packet = ""
    status = __Status.SIZE
    count = 0   # To make sure we get the correct amount of data.

    while True:
        if status == __Status.SIZE:
            size = sock.recv(6)  # Size data was sent without encryption.
            status = __Status.DATA

        if status == __Status.DATA:
            size = int(size)
            while size > 0:
                data = sock.recv(size)
                size -= len(data)
                packet += data.decode()
            status = __Status.COMPLETE

        if status == __Status.COMPLETE:
            dec_data = onetimepad.decrypt(packet, dec_key)
            l = json.loads(dec_data)
            tree.append(l)
            count += 1
            packet = ""
            status = __Status.SIZE

        if not size and count == layer:
            return tree


def fetch_path(sock: socket.SocketIO):
    """
    Fetching path and parsing it from the client side.
    Returns a tuple of path:str and layer:int
    """
    packet = ""
    count = 0   # To make sure that we receive exactly path & layer only.
    data = []
    status = __Status.SIZE

    while True:
        if status == __Status.SIZE:
            # Size was sent without any encryption.
            # Max number for an 8 bit is 255, thus the receive size is 3.
            size = sock.recv(3)
            status = __Status.DATA

        if status == __Status.DATA:
            size = int(size)
            while size > 0:
                read_byte = sock.recv(size)
                size -= len(read_byte)
                packet += read_byte.decode()

            status = __Status.COMPLETE

        if status == __Status.COMPLETE:
            data.append(int(packet))
            count += 1
            packet = ""
            status = __Status.SIZE

        if not size and count == 2:
            return (data[0], data[1])


def fetch_key(tree: List[List[int]], path: int, layer: int, height: int) -> str:
    """
    Generated the decision tree from the tree list only for the layer specified and 
    fetch the key.
    """
    # Tree only have the keys.
    # We generate the necessary decision tree from layer.
    # Then, we traverse generated OTP decision tree using the given path to obtain the key.

    # 1. Generate the necessary tree.
    decision_tree = []
    # 1-1. Generate all switches nodes.
    decision_tree.append(-1)
    for i in range(1, height):
        total_switch = 2 ** i
        while total_switch > 0:
            decision_tree.append(-1)
            total_switch -= 1

    # 1-2. Add all key memory nodes from succcess layer.
    key_nodes = tree[layer]
    assert len(key_nodes) == (2 ** height), "Key Nodes aren't complete."

    for key in key_nodes:
        decision_tree.append(key)

    # 1-3. Build the tree.
    root = build(decision_tree)

    # 2. Traverse the tree using the path.
    path_bin = bin(path)[2:]
    # Make sure len of path is appropriate.
    path_len = len(path_bin) - height
    if path_len < 0:
        # Meaning path's len is not to the length of tree.
        padding = "0" * abs(path_len)
        path_bin = padding + path_bin
        path_len = 0

    path_bin = path_bin[path_len:]
    key = __get_key(path_bin, root)

    return key


def __get_key(path_bin: str, node: Node) -> int:
    if node.value != -1:
        # Managed to reach memory node.
        return node.value

    for c in path_bin:
        if c == "0":
            return __get_key(path_bin[1:], node.left)
        else:
            return __get_key(path_bin[1:], node.right)

    return
