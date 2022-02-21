#!/usr/bin/env python3 

import otp_conn as oc
import secrets

layer = 128
height = 6
k = 80

# print(f"Receiving Decision tree, Layer: {layer}, Height: {height}")
# data = oc.recv_tree(layer, height)
# print(f"Decision Tree: {data}")

print(f"Generate OTP key from L:{layer}, H:{height}")
path = secrets.randbits(height)
fail_count = 0
while True:
  otp = oc.generate_otp_key(path, k)
  print(f"OTP: {otp}")
  if otp == "":
    print(f"Failed!, {fail_count}")
    fail_count += 1
  if fail_count == 11:
    break