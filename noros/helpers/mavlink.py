import argparse
import os
import sys
from ..node import Node
from pymavlink import mavutil
from pymavlink.dialects.v20 import all as mavlink


mavl = mavlink.MAVLink(None)


def MavlinkMessage(o):
    if isinstance(o, (bytes, bytearray)):
        msg = mavl.parse_char(o)
    else:
        msg = o.pack(mavl)
    return msg


def mavlink_bridge():
    parser = argparse.ArgumentParser()
    parser.add_argument('address', default="udp:localhost:14550",
                        help="The mavlink connection string", nargs='?')
    parser.add_argument('--topic_dir', '-t',
                        default="/mavlink", help="The topic directory")
    parser.add_argument('--dialect', '-d', default="all",
                        help="The mavlink dialect")
    parser.add_argument('--mavlink20', '-2',
                        action="store_true", help="Use mavlink 2.0")
    args = parser.parse_args()

    node = Node()

    if args.mavlink20:
        os.environ["MAVLINK20"] = "1"
    mavutil.set_dialect(args.dialect)
    mav = mavutil.mavlink_connection(args.address)

    pub_topic = node.publisher(args.topic_dir, bytes)
    topic_source = "{}/source".format(args.topic_dir)
    pub_source = node.publisher(topic_source, bytes)

    def cb_mav(sock):
        msg = mav.recv_msg()
        buf = msg.get_msgbuf()
        topic = msg.get_type().lower()
        topic = "{}/{}".format(args.topic_dir, topic)
        pub_topic.topic = topic
        pub_topic.send(buf)
        pub_source.send(buf)

    node.add_ext_socket(mav.fd, cb_mav)

    def send(msg):
        try:
            mav.mav.send(msg)
            return True
        except Exception as e:
            print(e, file=sys.stderr)
            return False

    def close():
        mav.close()
        node.shutdown()

    topic_sink = "{}/sink".format(args.topic_dir)
    sub_sink = node.subscriber(topic_sink, MavlinkMessage, callback=send)
    topic_close = "{}/close".format(args.topic_dir)
    sub_close = node.subscriber(topic_close, bytes, callback=close)
    topic_cmd = "{}/cmd".format(args.topic_dir)
    sv_cmd = node.service(topic_cmd, send, bool, MavlinkMessage)

    print("Publishing messages on", args.topic_dir, "from", args.address)
    node.spin()

    sub_sink.close()
    sv_cmd.close()
    sub_close.close()


if __name__ == '__main__':
    mavlink_bridge()
