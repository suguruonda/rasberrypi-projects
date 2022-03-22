import socket
import time
import struct
from contextlib import closing
import ipaddress

"""
print("Destination IP address:")
while True:
	try:
		print(">",end="")
		inputip = input()
		ipaddress.ip_address(inputip)
	except KeyboardInterrupt:
		exit()
	except:
		print('Incorrect IP address. Input IP address again.')
	else:
		break
"""			
host = '169.254.205.179'
#host = inputip
send_port = 60000

recv_ip = ""
recv_port = 60000

socksend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockrecv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockrecv.bind((recv_ip,recv_port))
i = 10
with closing(socksend), closing(sockrecv):
	while True:

		print('Waiting for recieve...')
		sr,addr = sockrecv.recvfrom(1024)
		r = struct.unpack(">i" , sr)[0]
		print("recieve: ", str(r))
		
		s = 1.0 /(2.0*r-1.0)
		if r % 2 == 0:
			s = -s 
		print("send: ", str(s))
		ss = struct.pack('>d', s)
		socksend.sendto(ss, (host,send_port))
