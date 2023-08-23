import argparse
import os
import time
import sys
import socket
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


def mavlink_router():
    parser = argparse.ArgumentParser()
    parser.add_argument('sink_topic', default="/mavlink/sink",
                        help="The topic points to sink", nargs='?')
    parser.add_argument('source_topic', default="/mavlink/source",
                        help="The topic points to source", nargs='?')
    parser.add_argument('address', default="udp:localhost:14551",
                        help="The mavlink connection string", nargs='?')
    parser.add_argument('--dialect', '-d', default="all",
                        help="The mavlink dialect")

    args = parser.parse_args()

    node = Node()
    mavutil.set_dialect(args.dialect)

    pub_sink = node.publisher(args.sink_topic, bytes)
    sub_source = node.subscriber(args.source_topic, bytes)

    method, addr, port = args.address.split(':')

    print("Routing messages to", args.address)

    if method == 'udp' or method == 'udpin':
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        def cb_sink(fd):
            buf = sock.recv(65535)
            pub_sink.send(buf)

        def cb_source(msg):
            try:
                sock.sendto(msg, (addr, int(port)))
            except Exception as e:
                print(e, file=sys.stderr)

        node.add_ext_socket(sock.fileno(), cb_sink)
        sub_source.callback = cb_source
    elif method == 'udpout':
        raise NotImplementedError
    elif method == 'tcp' or method == 'tcpout' or method == 'tcpin':
        raise NotImplementedError
    else:
        raise ValueError("Unknown method: {}".format(method))

    node.spin()


if __name__ == '__main__':
    mavlink_bridge()
