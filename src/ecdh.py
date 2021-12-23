from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

priv_a = ec.generate_private_key(ec.SECP256R1, default_backend())
#priv_a = priv_a.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())

pub_a = priv_a.public_key()
#pub_a = pub_a.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)

priv_b = ec.generate_private_key(ec.SECP256R1, default_backend())
#priv_b = priv_b.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())

pub_b = priv_b.public_key()
#pub_b = pub_b.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)

sec_a = priv_a.exchange(ec.ECDH(), pub_b)
sec_b = priv_b.exchange(ec.ECDH(), pub_a)

print(sec_a)
print(len(sec_a))
print(int.from_bytes(sec_a, "big"))

print(sec_b)
print(int.from_bytes(sec_b, "big"))
