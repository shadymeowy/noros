from noros import Node
from noros.helpers.mavlink import MavlinkMessage

node = Node()


def cb_ned(msg):
    print("ned: ", msg.x, msg.y, msg.z)


def cb_att(msg):
    print("att: ", msg.roll, msg.pitch, msg.yaw)


def cb_gps(msg):
    print("gps: ", msg.lat, msg.lon, msg.alt)


sub_ned = node.subscriber(
    '/mavlink/local_position_ned', MavlinkMessage, callback=cb_ned)
sub_att = node.subscriber(
    '/mavlink/attitude', MavlinkMessage, callback=cb_att)
sub_gps = node.subscriber(
    '/mavlink/global_position_int', MavlinkMessage, callback=cb_gps)

print("Subscriber started")

node.spin()
