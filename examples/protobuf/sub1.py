from noros import Node
from msg.position_pb2 import Position

node = Node()


def cb_pos(pos):
    print("Received:")
    print(pos)


sub_pos = node.subscriber('/uav/gps', Position, callback=cb_pos)

print("Subscriber started")
node.spin()

sub_pos.close()
node.close()