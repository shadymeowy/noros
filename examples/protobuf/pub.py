import time
from noros import Node, Rate

from msg.position_pb2 import Position
from msg.gps_pb2 import GPS

node = Node()
rate = Rate(30)

pub_position = node.publisher('/uav/position', Position)
pub_gps = node.publisher('/uav/gps', GPS)
pub_gps_pos = node.publisher('/uav/gps_pos', Position, GPS)

print("Publisher started")
pos = Position()
pos.x = 11
pos.y = 12
pos.z = 13

gps = GPS()
gps.latitude = 1.23
gps.longitude = 4.56


while True:
    try:
        pos.timestamp = time.time()
        pub_position.send(pos)
        pos.x += 1
        print("Sent:")
        print(pos, end='')
        # input()

        gps.timestamp = time.time()
        pub_gps.send(gps)
        gps.latitude += 1
        print("Sent:")
        print(gps, end='')
        # input()

        pub_gps_pos.send(pos, gps)
        print("Sent combined")
        # input()
        rate.sleep()
    except KeyboardInterrupt:
        break

print("Publisher stopped, cleaning up")
pub_gps_pos.close()
pub_gps.close()
pub_position.close()
node.close()