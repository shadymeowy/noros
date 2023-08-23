from noros import Node
from msg.position_pb2 import Position
from msg.gps_pb2 import GPS

node = Node()


def cb_gps_pos(gps, pos):
    print("Received:")
    print(gps)
    print(pos)


sub_position = node.subscriber('/uav/gps_pos', Position, GPS, callback=cb_gps_pos)

print("Subscriber started")
node.spin()
