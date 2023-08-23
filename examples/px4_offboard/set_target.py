import struct
from noros import Node

Position = struct.Struct('ddd')

node = Node()

sv_target = node.service_client('/set_target', bool, Position)
sv_target.wait_for_service()

print("Publisher started")

while True:
    pos = input("Enter position: ")
    pos = tuple(eval(pos))
    res = sv_target.call(pos)
    print("Response:", res)
