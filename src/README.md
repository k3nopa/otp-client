This explaination can be found [here](https://medium.com/@md.julfikar.mahmud/secure-socket-programming-in-python-d37b93233c69)
The proxy program used this [repo](git@github.com:Aludirk/tcp-proxy.git) as a reference to create current proxy.

# Modification ideas of paho.mqtt.client python file

## Functions or Variables to identify internal works

- This is needed to find which functions that need modifications.
- Find how to set new port if OTP is used.
    - default : 1883
    - TLS/SSL : 8883
    - OTP     : 6883

### Functions

#### TCP

- _sock_recv
- _sock_send
- _send_connect
    - _packet_queue
- _send_publish
    - _packet_queue
- _send_disconnect
    - _packet_queue
- _send_subscribe
    - _packet_queue
- _send_unsubscribe
_ _packet_write
_ _packet_read
    - _packet_handle
- _send_command_with_mid
    - _packet_queue

- _packet_queue
    - _sockpairW.send
    - _call_socket_register_write
- _packet_handle
    - _handle_pingreq
    - _handle_pingresq
    - _handle_pubackcomp
    - _handle_publish
    - _handle_pubrec
    - _handle_pubrel
    - _handle_connack
    - _handle_suback
    - _handle_unsuback


## Modification

- add Client class a new member variable (line: 610):
    - self.otp
