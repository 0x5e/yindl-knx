#!/usr/bin/env python
# coding=utf-8

import asyncio
import struct
import threading
import time
import logging

from .protocol import Yindl, Payload

_LOGGER = logging.getLogger(__name__)

class YindlClient():
  def __init__(self, host, port, user, psw, callback=None):
    self.host = host
    self.port = port
    self.user = user
    self.psw = psw
    self.knx_callback = callback

  async def run(self, loop):
    reader, writer = await asyncio.open_connection(self.host, self.port, loop=loop)
    self.reader = reader
    self.writer = writer

    self.login(self.user, self.psw)
    self.init_knx()
    self.heartbeat_thread = threading.Thread(target=self.heartbeat_loop, args=()).start()

    while True:
      pkg = await self.recv_pkg()
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

  async def recv_pkg(self):
    buf = await self.reader.read(11)
    length = struct.unpack('>H', buf[5:7])[0]
    buf += await self.reader.read(length - len(buf))
    _LOGGER.info('Recv <--- %s' % buf.hex())
    pkg = Yindl.parse(buf)
    return pkg.payload

  def send_pkg(self, obj):
    pkg = Yindl.build({'payload': obj})
    self.writer.write(pkg)

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
      _LOGGER.debug('KNX  <--- %s' % bytes(knx_telegram).hex())
      index = knx_telegram[3]
      self.knx_dict[index] = knx_telegram
      if self.knx_callback != None:
        self.knx_callback(knx_telegram)

  def knx_publish(self, knx_telegram_list):
    for knx_telegram in knx_telegram_list:
      _LOGGER.debug('KNX  ---> %s' % bytes(knx_telegram).hex())
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
    try:
      loop = asyncio.get_event_loop()
      if loop.is_running():
        self.run(loop)
      else:
        loop.run_until_complete(self.run(loop))
    finally:
      loop.close()
