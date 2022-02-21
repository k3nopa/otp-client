#!/usr/bin/env python3 

import otp_conn as oc

layer = 128
height = 7

print(f"Receiving Decision tree, Layer: {layer}, Height: {height}")
data = oc.recv_tree(layer, height)
print(f"Decision Tree: {data}")