import socket
import ecdh


def dh_do_handshake(sock: socket.SocketIO) -> bytes:
    client, _ = sock.accept()
    ec = ecdh.ECDH(client)

    # 1. Recv A (peer pub key)
    peer_pub = ec.recv_pub_key()

    # 2. Send B (pub key)
    pub = ec.export_key()
    ec.send_pub_key(pub)

    # 3. Generate Shared Key
    peer_pub_key = ec.import_key(peer_pub)
    share_key = ec.shared_key(peer_pub_key)
    return share_key


HOST = "127.0.0.1"
PORT = 8000


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)

    share_key = dh_do_handshake(s)
    print("K = ", share_key)

except KeyboardInterrupt:
    s.close()

finally:
    s.close()
