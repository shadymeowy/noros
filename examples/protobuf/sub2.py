from noros import Node
from msg.gps_pb2 import GPS

node = Node()


def cb_gps(gps):
    print("Received:")
    print(gps)


sub_gps = node.subscriber('/uav/gps', GPS, callback=cb_gps)

print("Subscriber started")
node.spin()

sub_gps.close()
node.close()