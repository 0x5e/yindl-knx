#!/usr/bin/env python
# coding=utf-8

import asyncore
import socket
import struct
import thread
import time
import logging
from protocol import Yindl, Payload

logging.basicConfig(format='%(asctime)s %(levelname)-5s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

class YindlClient(asyncore.dispatcher):

	def __init__(self, host, port, callback=None):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect((host, port))
		self.buffer = []
		self.knx_callback = callback

	def handle_connect(self):
		logging.info('Connected')
		self.login('yindl', '24325356658776987')
		self.init_knx()
		thread.start_new_thread(self.heartbeat_loop, ())

	def handle_close(self):
		logging.info('Closed')
		self.del_channel()
		self.close()

	def handle_read(self):
		pkg = self.recv_pkg()
		if pkg.type == 'Heartbeat_Ack':
			pass
		elif pkg.type == 'Login_Ack':
			logging.info('Login success')
		elif pkg.type == 'Init_KNX_Telegram_Reply':
			self.knx_update(pkg.data.knx_list)
			self.send_pkg({
				'type': 'Init_KNX_Telegram_Reply_Ack',
				'data': list(bytearray(Payload.build(pkg)[4:19])),
			})
			if pkg.data.index - 1 + pkg.data.count == pkg.data.amount:
				logging.info('KNX Telegrams all loaded, count: %d' % pkg.data.amount)
		elif pkg.type == 'KNX_Telegram_Event':
			self.knx_update(pkg.data.knx_list)
			self.send_pkg({
				'type': 'KNX_Telegram_Event_Ack',
				'data': list(bytearray(Payload.build(pkg)[4:12])),
			})

	def writable(self):
		if self.connected and len(self.buffer) == 0:
			return False
		return True

	def handle_write(self):
		pkg = self.buffer.pop(0)
		logging.debug('Send ---> %s' % pkg.encode('hex'))
		self.send(pkg)

	def recv_pkg(self):
		buf = self.recv(11)
		length = struct.unpack('>H', buf[5:7])[0]
		buf += self.recv(length - len(buf))
		logging.debug('Recv <--- %s' % buf.encode('hex'))
		pkg = Yindl.parse(buf)
		return pkg.payload

	def send_pkg(self, obj):
		pkg = Yindl.build({'payload': obj})
		self.buffer.append(pkg)

	def login(self, usr, psw):
		logging.info('Login')
		self.send_pkg({
			'type': 'Login',
			'data': {
				'usr': usr,
				'psw': psw,
			}
		})

	def init_knx(self):
		self.send_pkg({
			'type': 'Init_KNX_Telegram',
			'data': [0x00] * 13,
		})
		self.knx_dict = {}

	def heartbeat_loop(self):
		logging.info('Start heartbeat loop')
		while True:
			time.sleep(60)
			self.send_pkg({'type': 'Heartbeat', 'data': [0x7b]})

	def knx_update(self, knx_telegram_list):
		for knx_telegram in knx_telegram_list:
			knx_telegram = ''.join(map(chr, knx_telegram))
			logging.info('KNX  <--- %s' % knx_telegram.encode('hex'))
			index = knx_telegram[3]
			self.knx_dict[index] = knx_telegram
			if self.knx_callback != None:
				self.knx_callback(knx_telegram)

	def knx_publish(self, knx_telegram_list):
		for knx_telegram in knx_telegram_list:
			logging.info('KNX  ---> %s' % knx_telegram.encode('hex'))
		knx_telegram_list = map(bytearray, knx_telegram_list)
		knx_telegram_list = map(list, knx_telegram_list)
		self.send_pkg({
			'type': 'KNX_Telegram_Publish',
			'data': {
				'count': len(knx_telegram_list),
				'knx_list': knx_telegram_list,
			}
		})

def knx_publish_loop():
	raw_input()
	while True:
		knx_telegram = raw_input('Input KNX Telegram: ').decode('hex')
		if len(knx_telegram) != 11:
			continue
		client.knx_publish([knx_telegram])

if __name__ == '__main__':
	print('---------- SIEMENS Smart Home ----------')
	thread.start_new_thread(knx_publish_loop, ())
	client = YindlClient('192.168.1.251', 60002)
	asyncore.loop(timeout=0.5)
