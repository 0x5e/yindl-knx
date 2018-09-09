#!/usr/bin/env python
# coding=utf-8

import _thread

from protocol import *
from yindl import YindlClient

def pkg_compare(pkg, obj):
  pkg2 = Yindl.build(obj).hex()
  assert pkg == pkg2, '\n%s\n%s'%(pkg,pkg2)

heartbeat_pkg = 'ea61ea6001001500000000000000057b6aea62ea63'
heartbeat_obj = {
  'payload': {
    'type': 'Heartbeat',
    'data': [0x7b],
  }
}
pkg_compare(heartbeat_pkg, heartbeat_obj)

heartbeat_ack_pkg = 'ea61ea6001001500000000000100058494ea62ea63'
heartbeat_ack_obj = {
  'payload': {
    'type': 'Heartbeat_Ack',
    'data': [0x84],
  }
}
pkg_compare(heartbeat_ack_pkg, heartbeat_ack_obj)

login_pkg = 'ea61ea6001002e000000000500001e000579696e646c001132343332353335363635383737363938376fea62ea63'
login_obj = {
  'payload': {
    'type': 'Login',
    'data': {
      'usr':'yindl',
      'psw': '24325356658776987'
    },
  }
}
pkg_compare(login_pkg, login_obj)

login_ack_pkg = 'ea61ea6001001500000000050100050015ea62ea63'
login_ack_obj = {
  'payload': {
    'type': 'Login_Ack',
    'data': [0x00],
  }
}
pkg_compare(login_ack_pkg, login_ack_obj)

init_knx_telegram_pkg = 'ea61ea6001002100000000060300110000000000000000000000000034ea62ea63'
init_knx_telegram_obj = {
  'payload': {
    'type': 'Init_KNX_Telegram',
    'data': [0x00] * 13,
  }
}
pkg_compare(init_knx_telegram_pkg, init_knx_telegram_obj)

knx_telegram_event_pkg = 'ea61ea60010032000000000606002200000000000000020000000d0f0004004000000000000e0f00040000000050ea62ea63'
knx_telegram_event_obj = {
  'payload': {
    'type': 'KNX_Telegram_Event',
    'data': {
      'count': 0x0002,
      'knx_list': [
        [0x00, 0x00, 0x00, 0x0d, 0x0f, 0x00, 0x04, 0x00, 0x40, 0x00, 0x00],
        [0x00, 0x00, 0x00, 0x0e, 0x0f, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00],
      ]
    }
  }
}
pkg_compare(knx_telegram_event_pkg, knx_telegram_event_obj)



def knx_publish_loop():
  input()
  while True:
    knx_telegram = bytes.fromhex(input('Input KNX Telegram: '))
    if len(knx_telegram) != 11:
      continue
    client.knx_publish([knx_telegram])


if __name__ == '__main__':
  print('---------- SIEMENS Smart Home ----------')
  _thread.start_new_thread(knx_publish_loop, ())
  client = YindlClient('192.168.1.251', 60002, 'yindl', '24325356658776987')
  client.start()
