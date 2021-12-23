import socket
import selectors
import types

host = "127.0.0.1"
port = 1883

sel = selectors.DefaultSelector()
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen(5)
print("listening on", (host, port))
lsock.setblocking(False)
# listening socket, we want read events: selectors.EVENT_READ
sel.register(lsock, selectors.EVENT_READ, data=None)


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print("closing connection to", data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print("echoing", repr(data.outb), "to", data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


while True:
    # blocks until there are sockets ready for I/O
    events = sel.select(timeout=None)
    # mask is an event mask of the operations that are ready
    for key, mask in events:
        # key.data is None, then we know it’s from the listening socket and we need to accept() the connection.
        if key.data is None:
            # key.fileobj is the socket object
            accept_wrapper(key.fileobj)
        else:
            # a client socket that’s already been accepted
            service_connection(key, mask)
