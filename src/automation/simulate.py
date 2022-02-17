from paramiko import SSHClient, AutoAddPolicy
import time

# otp = '192.168.1.149'
# iot = '192.168.1.144'
otp = '192.168.0.20'
iot = '192.168.0.25'
user = 'pi'
passwd = 'Abang1998!'

otp_client = SSHClient()
iot_client = SSHClient()

otp_client.load_system_host_keys()
otp_client.set_missing_host_key_policy(AutoAddPolicy())

iot_client.load_system_host_keys()
iot_client.set_missing_host_key_policy(AutoAddPolicy())


try:

    for i in range(6, 61):
        otp_client.connect(otp, username=user, password=passwd)
        iot_client.connect(iot, username=user, password=passwd)
        print('[INFO] Sending OTP Commands')
        stdin, stdout, stderr = otp_client.exec_command('/home/pi/otp-circuit-mock/target/release/otp-conn &')
        time.sleep(1)
        print(f'[INFO] Sending IOT Commands, Sample{i}')
        stdin, stdout, stderr = iot_client.exec_command(f'/home/pi/iot/src/otp_test.py | tee /home/pi/iot/src/samples/a_1000_n_128_h_8/sample{i}.txt')
        stdout.readlines()  # Need to wait till the program finished.
        exit_stat = stdout.channel.recv_exit_status()

        if exit_stat == 0:
            print("[INFO] Success!")
            stdin, stdout, stderr = otp_client.exec_command('kill $(pgrep -f otp)')
            stdin, stdout, stderr = iot_client.exec_command('kill $(pgrep -f otp)')
            print(f"[Error] {stderr.readlines()}")

        stdin.close()
        stdout.close()
        stderr.close()
        otp_client.close()
        iot_client.close()
        time.sleep(1)


finally:
    stdin, stdout, stderr = otp_client.exec_command('kill $(pgrep -f otp)')
    stdin, stdout, stderr = iot_client.exec_command('kill $(pgrep -f otp)')

    stdin.close()
    stdout.close()
    stderr.close()

    otp_client.close()
    iot_client.close()
