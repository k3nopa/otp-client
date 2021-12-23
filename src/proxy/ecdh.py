from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, types
import socket


class ECDH:
    def __init__(self, sock: socket.SocketIO) -> None:
        self.sock = sock
        self.priv = ec.generate_private_key(ec.SECP256R1, default_backend())
        self.pub = self.priv.public_key()

    def import_key(self, key: bytes) -> types.PUBLIC_KEY_TYPES:
        """
        Import a PEM formatted Public Key and return in EllipticCurvePublicKey class type.
        """
        return serialization.load_pem_public_key(key, backend=default_backend())

    def export_key(self) -> bytes:
        """
        Export Public Key to PEM format.
        """
        return self.pub.public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def send_pub_key(self, pub_key: bytes):
        """
        Format and send public key to client/server.
        """
        self.sock.send(f"{len(pub_key)}".encode())
        self.sock.send(pub_key)

    def recv_pub_key(self) -> bytes:
        """
        Recv and format public key from client/server.
        """
        # Assume length of bytes are 5.
        data_len = self.sock.recv(5).decode()
        data_len = int(data_len.replace("-", ""))

        data = self.sock.recv(data_len)

        # In Case when some data loss happen.
        if len(data) != data_len:
            remain_str = "-" * (data_len - len(data))
            data = remain_str.encode() + data

        return data

    def shared_key(self, peer_public: ec.EllipticCurvePublicKey):
        return self.priv.exchange(ec.ECDH(), peer_public)
