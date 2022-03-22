import socket
import time
import struct
from contextlib import closing
host = '169.254.205.179'

port = 60000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
i = 10
with closing(sock):
	while i > 0:
		"""
		message = 'Hell via UDP'.encode('utf-8')
		print("send: ",message)
		sock.sendto(message, (host,port))
		"""
		d = 193193193
		ds = struct.pack('>d',d)
		print('send: ',ds)
		sock.sendto(ds, (host,port))
		
		time.sleep(1)
		i -= 1
