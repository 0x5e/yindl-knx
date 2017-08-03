#!/usr/bin/env python
# coding=utf-8

import socket
import struct
import time
from protocol import Yindl, Payload

class YindlClient():
	def __init__(self, host, port):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.addr = (host, port)

	def connect(self):
		print('Connecting to %s:%d' % self.addr)
		self.sock.connect(self.addr)
		print('Connected')

	def send_pkg(self, obj):
		pkg = Yindl.build({'payload': obj})
		self.sock.sendall(pkg)

	def recv_pkg(self):
		buf = self.sock.recv(11)
		length = struct.unpack('>H', buf[5:7])[0]
		buf += self.sock.recv(length - len(buf))
		pkg = Yindl.parse(buf)
		return pkg.payload

	def login(self, usr, psw):
		print('Login')
		self.send_pkg({
			'type': 'Login',
			'data': {
				'usr': usr,
				'psw': psw,
			}
		})

		login_ack = self.recv_pkg()
		assert login_ack.type == 'Login_Ack'
		print('Login success')


	def init_knx(self):
		self.send_pkg({
			'type': 'Init_KNX_Telegram',
			'data': [0x00] * 13,
		})

		self.knx_list = []
		while True:
			pkg = self.recv_pkg()
			assert pkg.type == 'Init_KNX_Telegram_Reply'

			self.knx_list += pkg.data.knx_list

			self.send_pkg({
				'type': 'Init_KNX_Telegram_Reply_Ack',
				'data': struct.unpack('>15B', Payload.build(pkg)[4:19]),
			})
			if pkg.data.index - 1 + pkg.data.count == pkg.data.amount:
				break
		print('KNX Telegrams loaded, count: %d' % len(self.knx_list))

	def heartbeat_loop(self):
		while True:
			time.sleep(60)
			self.send_pkg({'type': 'Heartbeat', 'data': [0x7b]})
			pkg = self.recv_pkg()
			assert pkg.type == 'Heartbeat_Ack'

print('---------- SIEMENS Smart Home ----------')
client = YindlClient('192.168.1.251', 60002)
client.connect()
client.login('yindl', '24325356658776987')
client.init_knx()


