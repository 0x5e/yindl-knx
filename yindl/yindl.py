#!/usr/bin/env python
# coding=utf-8

import asyncore
import socket
import struct
import _thread
import time
import logging

from .protocol import Yindl, Payload

_LOGGER = logging.getLogger(__name__)

class YindlClient(asyncore.dispatcher):

  def __init__(self, host, port, user, psw, callback=None):
    asyncore.dispatcher.__init__(self)
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.connect((host, port))
    self.user = user
    self.psw = psw
    self.buffer = []
    self.knx_callback = callback

  def handle_connect(self):
    _LOGGER.info('Connected')
    self.login(self.user, self.psw)
    self.init_knx()
    self.heartbeat_thread = _thread.start_new_thread(self.heartbeat_loop, ())

  def handle_close(self):
    _LOGGER.info('Closed')
    self.del_channel()
    self.close()

  def handle_read(self):
    pkg = self.recv_pkg()
    if pkg.type == 'Heartbeat_Ack':
      pass
    elif pkg.type == 'Login_Ack':
      _LOGGER.info('Login success')
    elif pkg.type == 'Init_KNX_Telegram_Reply':
      self.knx_update(pkg.data.knx_list)
      self.send_pkg({
        'type': 'Init_KNX_Telegram_Reply_Ack',
        'data': list(bytearray(Payload.build(pkg)[4:19])),
      })
      if pkg.data.index - 1 + pkg.data.count == pkg.data.amount:
        _LOGGER.info('KNX Telegrams all loaded, count: %d' % pkg.data.amount)
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
    _LOGGER.debug('Send ---> %s' % pkg.hex())
    self.send(pkg)

  def recv_pkg(self):
    buf = self.recv(11)
    length = struct.unpack('>H', buf[5:7])[0]
    buf += self.recv(length - len(buf))
    _LOGGER.debug('Recv <--- %s' % buf.hex())
    pkg = Yindl.parse(buf)
    return pkg.payload

  def send_pkg(self, obj):
    pkg = Yindl.build({'payload': obj})
    self.buffer.append(pkg)

  def login(self, usr, psw):
    _LOGGER.info('Login')
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

  def knx_update(self, knx_telegram_list):
    for knx_telegram in knx_telegram_list:
      _LOGGER.info('KNX  <--- %s' % bytes(knx_telegram).hex())
      index = knx_telegram[3]
      self.knx_dict[index] = knx_telegram
      if self.knx_callback != None:
        self.knx_callback(knx_telegram)

  def knx_publish(self, knx_telegram_list):
    for knx_telegram in knx_telegram_list:
      _LOGGER.info('KNX  ---> %s' % bytes(knx_telegram).hex())
    knx_telegram_list = map(bytearray, knx_telegram_list)
    knx_telegram_list = map(list, knx_telegram_list)
    self.send_pkg({
      'type': 'KNX_Telegram_Publish',
      'data': {
        'count': len(knx_telegram_list),
        'knx_list': knx_telegram_list,
      }
    })

  def heartbeat_loop(self):
    _LOGGER.info('Start heartbeat loop')
    while True:
      time.sleep(60)
      self.send_pkg({'type': 'Heartbeat', 'data': [0x7b]})

  def start(self):
    asyncore.loop(timeout=15.0)
