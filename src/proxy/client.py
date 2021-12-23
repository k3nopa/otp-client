import socket
import ecdh


def dh_handle_handshake(sock: socket.SocketIO) -> bytes:
    ec = ecdh.ECDH(sock)

    # 1. Send A (pub key)
    pub = ec.export_key()
    ec.send_pub_key(pub)

    # 2. Recv B (peer pub key)
    peer_pub = ec.recv_pub_key()

    # 3. Generate Shared Key
    peer_pub_key = ec.import_key(peer_pub)
    share_key = ec.shared_key(peer_pub_key)
    return share_key


HOST = "127.0.0.1"
PORT = 8000


try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    share_key = dh_handle_handshake(sock)
    print("K = ", share_key)

except KeyboardInterrupt:
    sock.close()

finally:
    sock.close()
