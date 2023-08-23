import zmq
from .serialization import deserializer


class Subscriber:
    def __init__(self, socket, node, topic, callback, protos):
        if isinstance(topic, str):
            topic = topic.encode('utf-8')
        self._topic = topic + b'$'
        self.node = node
        self.socket = socket

        self.set_callback(callback)
        self.protos = list(protos)
        for i, proto in enumerate(self.protos):
            self.protos[i] = deserializer(proto)
        self.socket.setsockopt_string(
            zmq.SUBSCRIBE, self._topic.decode('utf-8'))

    @property
    def topic(self):
        return self._topic.strip(b'$')

    def recv(self, flags=0):
        res = self.socket.recv_multipart(flags=flags)
        l = len(res)
        if l >= 2:
            topic, bytss = res[0], res[1:]
            topic = topic.decode('utf-8')
            if not topic.startswith(self._topic.decode('utf-8')):
                raise ValueError("Invalid topic: {}".format(topic))
            msgs = []
            for proto, byts in zip(self.protos, bytss):
                msgs.append(proto(byts))
            self.callback(*msgs)
            return msgs
        elif l == 1:
            self.callback()
        else:
            raise ValueError("Invalid message: {}".format(res))

    def recv_all(self):
        msgs = []
        while True:
            try:
                msg = self.recv(zmq.NOBLOCK)
            except zmq.Again:
                break
            if msg is not None:
                msgs.append(msg)
        return msgs

    def set_callback(self, callback):
        if callback is None:
            self.callback = lambda *x: x
        else:
            self.callback = callback

    def close(self):
        self.socket.close()
        self.node.subs.remove(self)
