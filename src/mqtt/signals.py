import serial
import secrets
import time
import struct
from enum import Enum, auto

class Status(Enum):
    R_SIZE = auto()
    R_DATA = auto()
    COMPLETE = auto()
    RETRY = auto()

def __send_path(ser, height):
    path = secrets.randbits(height)
    length = len(f"{path}")
    ser.write(f"{length}".encode())

    time.sleep(.5)
    ser.write(f"{path}".encode())
    return path

def recv_key(ser, height) -> int:
    path = __send_path(ser, height)

    key = []
    str_num = ''
    size = 0
    fail_count = 0

    ser.flushInput()
    ser.flushOutput()
    status = Status.R_SIZE

    while True:
        if ser.inWaiting() > 0:
            r = ser.read()
            if status == Status.R_SIZE:
                i, = struct.unpack(">B", r)
                size = int(i)
                if size == 0:
                    status = Status.RETRY
                else:
                    status = Status.R_DATA

            elif status == Status.R_DATA:
                i, = struct.unpack(">B", r)
                key.append(int(i))
                size -= 1
                if size == 0:
                    status = Status.COMPLETE

            elif status == Status.RETRY:
                path = __send_path(ser, height)
                fail_count += 1
                print(f"[{fail_count}th] retry with ", path)
                status = Status.R_SIZE

            if status == Status.COMPLETE:
                for k in key:
                    str_num += str(k)
                break

            if fail_count == 300:
                str_num = 0
                break
        
    return (path, int(str_num))

def recv_layer(ser) -> int:
    key = []
    size = 0

    ser.flushInput()
    ser.flushOutput()

    # __send_path(ser, 7)

    status = Status.R_SIZE
    while True:
        if ser.inWaiting() > 0:
            r = ser.read()
            if status == Status.R_SIZE:
                i, = struct.unpack(">B", r)
                size = int(i)
                status = Status.R_DATA

            elif status == Status.R_DATA:
                i, = struct.unpack(">B", r)
                key.append(int(i))
                size -= 1
                if size <= 0:
                    status = Status.COMPLETE

            if status == Status.COMPLETE:
                break
        
    return key

def recv_otp(ser, layers: int, height: int) :
    tmp = []    # Holds the bytes of 1 key.
    key = []    # Holds the keys for 1 tree.
    tree = []   # Holds all the keys for all trees.
    count = 0
    total_keys = 2**height  # Total keys for each layer

    ser.flushInput()
    ser.flushOutput()

    start = time.time()
    while True:
        if ser.inWaiting() > 0:
            r = ser.read()
            i, = struct.unpack(">B", r)
            tmp.append(int(i))
        
        elif len(tmp) == 4:
            # Received complete a key.
            num = 0
            for i in range(4):
                num = (num << 8) | tmp[i]

            # print(f"{num}: {tmp}")
            tmp = []
            key.append(num)
            count += 1
        
        if count == total_keys:
            # Received complete 1 tree's key values.
            tree.append(key)
            key = []
            count = 0

        if len(tree) == layers:
            # Received complete whole decision tree's key values.
            break
    
    end = time.time()
    print(f"Time Taken: {end-start}s")
    return tree

if __name__ == "__main__":
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )

    try:
        res = recv_otp(ser, 5, 7)

        assert len(res) == 5, "Total Length not 128"

        for i in range(len(res)):
            assert len(res[i]) == 128, f"Total Keys are not 128 in Layer {i}"


    except KeyboardInterrupt:
        print("Exited")

    except Exception as e:
        print(e)

    finally: 
        ser.close()

