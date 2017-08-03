-- http://www.yindl.com/apps/apple/econtrol/
-- Personal Plugins: ~/.config/wireshark/plugins/

local p_yindl = Proto("yindl", "Yindl KNX protocol (SIEMENS Smart Home over TCP)") -- 

local f_ver = ProtoField.uint8("yindl.ver", "Version", base.HEX)
local f_len = ProtoField.uint16("yindl.len", "Length", base.HEX)
local f_seq = ProtoField.uint32("yindl.seq", "Sequence number", base.HEX)
local f_payload = ProtoField.bytes("yindl.payload", "Payload")

local types = {
	[0x0000] = "Heartbeat", [0x0001] = "Heartbeat Ack",
	[0x0500] = "Login", [0x0501] = "Login Ack",

	[0x0603] = "Init KNX Telegram",
	[0x0604] = "Init KNX Telegram Reply", -- multipart
	[0x0605] = "Init KNX Telegram Reply Ack",

	[0x0606] = "KNX Telegram Event",
	[0x0607] = "KNX Telegram Event Ack",
	[0x0608] = "KNX Telegram Publish",
	[0x0609] = "KNX Telegram Publish Ack",
}

local f_payload_type = ProtoField.uint16("yindl.payload.type", "Type", base.HEX, types)
local f_payload_len = ProtoField.uint16("yindl.payload.len", "Length", base.HEX)
local f_payload_data = ProtoField.bytes("yindl.payload.data", "Data")
local f_payload_bcc = ProtoField.uint8("yindl.payload.bcc", "BCC", base.HEX)

local f_payload_user = ProtoField.string("yindl.payload.user", "Username")
local f_payload_pass = ProtoField.string("yindl.payload.pass", "Password")
local f_payload_amount = ProtoField.uint64("yindl.payload.amount", "Amount", base.HEX)
local f_payload_index = ProtoField.uint64("yindl.payload.index", "Index", base.HEX)
local f_payload_count = ProtoField.uint64("yindl.payload.count", "Count", base.HEX)
local f_payload_knx = ProtoField.bytes("yindl.payload.knx", "KNX Telegram")

p_yindl.fields = {
	f_ver, f_len, f_seq, f_payload,
	f_payload_type, f_payload_len, f_payload_data, f_payload_bcc,
	f_payload_user, f_payload_pass,
	f_payload_amount, f_payload_index, f_payload_count, f_payload_knx,
}

local data_dis = Dissector.get("data")

local function SmartHome_dissector(buf, pkt, root)
	local buf_len = buf:len()
	if buf_len <= 15 then
		return false
	end

	local v_stx = buf(0, 4)
	local v_etx = buf(buf_len - 4, 4)
	if v_stx:bytes() ~= ByteArray.new("ea 61 ea 60") or v_etx:bytes() ~= ByteArray.new("ea 62 ea 63") then
		return false
	end

	pkt.cols.protocol = p_yindl.name

	local v_ver = buf(4, 1)
	local v_len = buf(5, 2)
	local v_seq = buf(7, 4)
	local v_payload = buf(11, buf_len - 15)
	local v_payload_type = buf(11, 2)
	local v_payload_len = buf(13, 2)
	local v_payload_data = buf(15, v_payload_len:uint() - 4)
	local v_payload_bcc = buf(11 + v_payload_len:uint(), 1)

	local tree = root:add(p_yindl, buf())
	tree:add(f_ver, v_ver)
	tree:add(f_len, v_len)
	tree:add(f_seq, v_seq)

	local subtree = tree:add(f_payload, v_payload)
	subtree:set_text(string.format("Payloads: (%d bytes)", v_payload:len()))
	subtree:add(f_payload_type, v_payload_type)
	subtree:add(f_payload_len, v_payload_len)

	local datatree = subtree:add(f_payload_data, v_payload_data)
	datatree:append_text(string.format(" (%d bytes)", v_payload_data:len()))

	local i_payload_type = v_payload_type:uint()
	if i_payload_type == 0x0500 then
		local user_len = v_payload_data(0, 2):uint()
		local pass_len = v_payload_data(user_len + 2, 2):uint()
		local v_user = v_payload_data(2, user_len)
		local v_pass = v_payload_data(user_len + 4, pass_len)

		datatree:add(f_payload_user, v_user)
		datatree:add(f_payload_pass, v_pass)
	elseif i_payload_type == 0x0604 or i_payload_type == 0x0605 then
		local v_amount = v_payload_data(6, 4)
		datatree:add(f_payload_amount, v_amount)

		local v_index = v_payload_data(10, 4)
		datatree:add(f_payload_index, v_index)

		local v_count = v_payload_data(14, 1)
		datatree:add(f_payload_count, v_count)

		if i_payload_type == 0x0604 then
			for i=0,v_count:uint() - 1 do
				datatree:add(f_payload_knx, v_payload_data(15 + i * 11, 11))
			end
		end
	elseif i_payload_type == 0x0606 or i_payload_type == 0x0608 then
		local v_count = v_payload_data(0, 8)
		datatree:add(f_payload_count, v_count)
		for i=0,v_count:uint64():tonumber()-1 do
			datatree:add(f_payload_knx, v_payload_data(8 + i * 11, 11))
		end
	end

	subtree:add(f_payload_bcc, v_payload_bcc)

	return true
end

function p_yindl.dissector(buf, pkt, root) 
	if SmartHome_dissector(buf,pkt,root) then
		return
	end
	data_dis:call(buf,pkt,root)
end

local tcp_table = DissectorTable.get("tcp.port")
tcp_table:add(60002, p_yindl)
