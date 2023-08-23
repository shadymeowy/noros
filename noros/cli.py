import argparse
import zmq


def handler(sub_conn, pub_conn):
    context = zmq.Context()
    frontend = context.socket(zmq.XSUB)
    frontend.bind(pub_conn)

    backend = context.socket(zmq.XPUB)
    backend.bind(sub_conn)

    zmq.proxy(frontend, backend)


def list_topics(sub_conn, pub_conn):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(sub_conn)
    socket.setsockopt_string(zmq.SUBSCRIBE, '')
    raw_topics = []
    try:
        while True:
            byts = socket.recv_multipart()[0]
            topic = byts.decode('utf-8').strip('$')
            if topic not in raw_topics:
                print(topic)
                raw_topics.append(topic)
    except KeyboardInterrupt:
        pass

    raw_topics.sort()

    topics = []
    services = {}
    for topic in raw_topics:
        if not '@' in topic:
            topics.append(topic)
        elif topic.endswith('@'):
            topic = topic.strip('@')
            services[topic] = []
        else:
            topic, uid = topic.split('@')
            services[topic].append(uid)

    print("\n\nTotal number of topics is {}:".format(len(topics)))
    topics = list(topics)
    topics.sort()
    for topic in topics:
        print('\t', topic)

    print("\nTotal number of services is {}:".format(len(services)))
    for topic, uids in services.items():
        print('\t', topic)
        for uid in uids:
            print('\t\t', uid)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'method',
        choices=['handler', 'list'],
        help="The method to run")
    parser.add_argument(
        '--sub_conn', '-s',
        default="ipc:///tmp/sub",
        help="The connection string for the subscriber")
    parser.add_argument(
        '--pub_conn', '-p',
        default="ipc:///tmp/pub",
        help="The connection string for the publisher")
    args = parser.parse_args()

    if args.method == 'handler':
        handler(args.sub_conn, args.pub_conn)
    elif args.method == 'list':
        list_topics(args.sub_conn, args.pub_conn)
    else:
        raise ValueError("Unknown method: {}".format(args.method))
