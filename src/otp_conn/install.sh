#!/usr/bin/bash

maturin build && pip install --force-reinstall /home/pi/iot/src/otp_conn/target/wheels/*.whl