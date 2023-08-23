import struct
from noros import Node
from noros.helpers.mavlink import mavl, mavlink, MavlinkMessage

Position = struct.Struct('ddd')

node = Node()

pub_sink = node.publisher('/mavlink/sink', MavlinkMessage)

sub_hearthbeat = node.subscriber('/mavlink/heartbeat', MavlinkMessage)
sub_gps = node.subscriber('/mavlink/global_position_int', MavlinkMessage)
sub_ack = node.subscriber('/mavlink/command_ack', MavlinkMessage)
sub_ned = node.subscriber('/mavlink/local_position_ned', MavlinkMessage)

print("Waiting for services")
sv_cmd = node.service_client('/mavlink/cmd', bool, MavlinkMessage)
sv_cmd.wait_for_service()

print("Waiting for heartbeat")
sub_hearthbeat.recv()
print("Received heartbeat")

print("Waiting for gps")
sub_gps.recv()
print("Received gps")


target_system = 1
target_component = 1


def wait_ack(command):
    while True:
        msg = sub_ack.recv()[0]
        if msg.command == command:
            break


def set_mode(base_mode, custom_mode, custom_sub_mode):
    mode_msg = mavl.command_long_encode(
        target_system,
        target_component,
        mavlink.MAV_CMD_DO_SET_MODE,
        0,
        base_mode,
        custom_mode,
        custom_sub_mode,
        0, 0, 0, 0)
    sv_cmd.call(mode_msg)
    wait_ack(mavlink.MAV_CMD_DO_SET_MODE)


def set_arm(arm=True):
    arm_msg = mavl.command_long_encode(
        target_system,
        target_component,
        mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1 if arm else 0,
        0, 0, 0, 0, 0, 0)
    sv_cmd.call(arm_msg)
    wait_ack(mavlink.MAV_CMD_COMPONENT_ARM_DISARM)


def send_setpoint(x, y, z):
    msg_setpoint = mavl.set_position_target_local_ned_encode(
        0,
        target_system,
        target_component,
        mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111111000,
        x, y, z, 0, 0, 0,
        0, 0, 0,
        0, 0)
    pub_sink.send(msg_setpoint)


print("Arming")
set_arm(True)

print("Dumping position queue")
sub_ned.recv_all()

print("Sending initial set points")
for i in range(100):
    send_setpoint(0, 0, 0)
    sub_ned.recv()

print("Switching to offboard")
set_mode(29, 6, 0)

tx, ty, tz = 0, 0, -1
x, y, z = 0, 0, 0
max_dist = 5


def cb_ned(pos):
    global x, y, z
    x, y, z = pos.x, pos.y, pos.z
    print("ned: ", x, y, z)
    d = (x - tx)**2 + (y - ty)**2 + (z - tz)**2
    d **= 0.5
    if d > max_dist:
        sx = (tx - x) / d * max_dist + x
        sy = (ty - y) / d * max_dist + y
        sz = (tz - z) / d * max_dist + z
    else:
        sx = tx
        sy = ty
        sz = tz
    print("setpoint: ", sx, sy, sz)
    send_setpoint(sx, sy, sz)


def set_target(pos):
    global tx, ty, tz
    if pos[2] > 0:
        return False
    tx, ty, tz = pos
    return True


sub_ned.set_callback(cb_ned)
sv_target = node.service('/set_target', set_target, bool, Position)

node.spin()
