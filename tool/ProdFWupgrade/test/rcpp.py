import socket
import struct

CAMERA_IP = "192.168.7.38"
RCP_PORT = 1756

# 組合 16-Byte RCP+ Header (Big-Endian)
# 範例：讀取 Virtual Alarm #1 狀態 (Tag: 0x0a8b, Type: F_FLAG(0x00), Ver: 3, Dir: READ(0))
tag = 0x0A8B
data_type = 0x00  # F_FLAG
ver_rw = (3 << 4) | 0  # Version 3, READ (0)
action_res = 0x0000
client_id = 0x0000
session_id = 0x00000000
num_desc = 1  # Alarm #1

header = struct.pack(
    ">HBBHHII",
    tag,
    data_type,
    ver_rw,
    action_res,
    client_id,
    session_id,
    num_desc,
)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.settimeout(5.0)
  s.connect((CAMERA_IP, RCP_PORT))
  s.sendall(header)

  # 接收回應封包
  response = s.recv(1024)
  print("Raw Hex Response:", response.hex())
