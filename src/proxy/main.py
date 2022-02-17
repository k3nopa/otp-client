import signal
import socket
import threading
import proxy

shutdownEvent = threading.Event()


def exit_handler(signal, frame):
    print(" Exited Gracefully")
    shutdownEvent.set()


def main():

    signal.signal(signal.SIGINT, exit_handler)
    client = "0.0.0.0"  # MQTT Client Address
    server = "127.0.0.1"  # MQTT Broker Address
    port = 1883
    otp = True
    otp_layer = 128
    otp_height = 7

    try:
        proxy_handler = proxy.Proxy(
            client, server, port, shutdownEvent, otp, otp_layer, otp_height
        )
        proxy_handler.daemon = True
        proxy_handler.start()

        print(
            f"Proxy established: upstream ({client}:{port}) <-> downstream ({server}:{port})"
        )

        while proxy_handler.is_alive():
            proxy_handler.join(0.05)

        return proxy_handler.err

    except socket.gaierror as e:
        print(f"Fail to initialize proxy (socket.gaierror: {e}).")

    except RuntimeError as e:
        print(f'"{e}" is not supported.')

    return 1


if __name__ == "__main__":
    main()
