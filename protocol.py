#!/usr/bin/env python
# coding=utf-8

from construct import *

LoginQuery = Struct(
	'usr' / PascalString(Int16ub),
	'psw' / PascalString(Int16ub),
)

KNXTelegram = Byte[11]

KNXReply = Struct(
	'unknown' / Byte[6],
	'amount' / Int32ub,
	'index' / Int32ub,
	'count' / Int8ub,
	'knx_list' / KNXTelegram[this.count]
)

KNXEvent = Struct(
	'count' / Default(Int64ub, 0x0000000000000000),
	'knx_list' / KNXTelegram[this.count],
)

Payload = Struct(
	'type' / Enum(Int16ub,
		Heartbeat = 0x0000,
		Heartbeat_Ack = 0x0001,
		Login = 0x0500,
		Login_Ack = 0x0501,
		Init_KNX_Telegram = 0x0603,
		Init_KNX_Telegram_Reply = 0x0604,
		Init_KNX_Telegram_Reply_Ack = 0x0605,
		KNX_Telegram_Event = 0x0606,
		KNX_Telegram_Event_Ack = 0x0607,
		KNX_Telegram_Publish = 0x0608,
		KNX_Telegram_Publish_Ack = 0x0609,
	),
	'len' / Default(Int16ub, 0x0000),
	'data' / Switch(this.type, {
		'Login': LoginQuery,
		'Login_Ack': Const(Byte[1], [0x00]),
		'Init_KNX_Telegram': Byte[13],
		'Init_KNX_Telegram_Reply': KNXReply,
		'KNX_Telegram_Event': KNXEvent,
		'KNX_Telegram_Publish': KNXEvent,
	}, default=Byte[len_(this.data)]),
	'bcc' / Default(Int8ub, 0x00),
)

_Yindl = Struct(
	Const(Int32ub, 0xea61ea60),
	'ver' / Default(Int8ub, 0x01),
	'len' / Default(Int16ub, 0x0000),
	'seq' / Default(Int32ub, 0x00000000),
	'payload' / Payload,
	Const(Int32ub, 0xea62ea63),
)

class YindlConstruct():
	def bcc_checksum(self, payload):
		bcc = 0x00
		for x in xrange(0,len(payload)):
			bcc ^= ord(payload[x])
		return bcc

	def build(self, obj):
		pkg = _Yindl.build(obj)
		obj['len'] = len(pkg)
		obj['payload']['len'] = len(pkg) - 16

		pkg = _Yindl.build(obj)
		obj['payload']['bcc'] = self.bcc_checksum(pkg[4:-5])

		return _Yindl.build(obj)

	def parse(self, context):
		return _Yindl.parse(context)

Yindl = YindlConstruct()
