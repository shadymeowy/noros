from .serialization import serializer


class Publisher:
    def __init__(self, socket, node, topic, callback, protos):
        self.topic = topic
        self.node = node
        self.socket = socket
        self.protos = list(protos)
        for i, proto in enumerate(self.protos):
            self.protos[i] = serializer(proto)
        self.set_callback(callback)

    @property
    def topic(self):
        return self._topic.strip(b'$')

    @topic.setter
    def topic(self, topic):
        if isinstance(topic, str):
            topic = topic.encode('utf-8')
        self._topic = topic + b'$'

    def send(self, *msgs):
        msgs = self.callback(*msgs)
        if msgs is None:
            return
        bytss = [self._topic]
        if len(msgs) > len(self.protos):
            raise ValueError("Too many messages")
        for msg, proto in zip(msgs, self.protos):
            byts = proto(msg)
            if byts is None:
                raise ValueError("Invalid message: {}".format(msg))
            bytss.append(byts)
        self.socket.send_multipart(bytss)

    def set_callback(self, callback):
        if callback is None:
            self.callback = lambda *x: x
        else:
            self.callback = callback

    def close(self):
        self.socket.close()
        self.node.pubs.remove(self)
