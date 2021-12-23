import struct
from enum import Enum
import onetimepad
import binascii
import base64

one = b'\x02\x00\x00\x90\x03\x00\x01\x00'
two = b'\xe0\x00'
three = b'\x90\x00'
four = b'0\x12\x00\x0ehome/test/bulbON'

PacketType = {
    0x10 : "CONNECT",
    0x20 : "CONNACK",
    0x30 : "PUBLISH",
    0x40 : "PUBACK",
    0x50 : "PUBREC",
    0x60 : "PUBREL",
    0x70 : "PUBCOMP",
    0x80 : "SUBSCRIBE",
    0x90 : "SUBACK",
    0xA0 : "UNSUBSCRIBE",
    0xB0 : "UNSUBACK",
    0xC0 : "PINGREQ",
    0xD0 : "PINGRESP",
    0xE0 : "DISCONNECT"
}


# Packet is big endian format.
def parser(data):
    fixed_header = struct.unpack('!B', data[:1])
    fixed_header = fixed_header[0]
    #print("Data : ", data,"Fixed Header : ", hex(fixed_header))

    try:
        return (PacketType[fixed_header], data)
    except Exception as e:
        # Means that there are flags in 1st byte.
        # 240 = b'1111_0000'
        return (PacketType[fixed_header & 240], data)

#parser(four)
#print(four[:1])
#
#enc = onetimepad.encrypt(four[:1].hex(), "secret")
#
#byte_val = binascii.unhexlify(enc)
##base_val = base64.standard_b64encode(byte_val)
#print(enc, byte_val)
#
##out_header = struct.pack('!2s', binascii.unhexlify(enc))
#out_header = binascii.unhexlify(enc)
#
#print(out_header)
#
#out_header = struct.unpack('!2s', out_header)
#print(out_header[0].hex()) 
