import zmq
import time
from uuid import uuid4


class ServiceClient:
    def __init__(self, node, topic, callback, ret_proto, protos):
        if isinstance(topic, str):
            topic = topic.encode('utf-8')
        self._topic = topic + b'@'
        self.uid = uuid4().hex.encode('utf-8')
        self.sub = node.subscriber(self._topic + self.uid, bytes, ret_proto)
        self.pub = node.publisher(self._topic, bytes, bytes, *protos)
        self.node = node
        self.set_callback(callback)

    def call(self, *msgs):
        muid = uuid4().bytes
        self.pub.send(self.uid, muid, *msgs)
        while True:
            res = self.sub.recv()
            if res is not None:
                break
        muid2 = res[0]
        res = res[1] if len(res) == 2 else None
        if muid != muid2:
            raise ValueError("Service message uuid mismatch")
        self.callback(res)
        return res

    def wait_for_service(self):
        while True:
            self.pub.send(self.uid)
            try:
                self.sub.recv(zmq.NOBLOCK)
                break
            except zmq.Again:
                pass
            time.sleep(0.1)

    def set_callback(self, callback):
        if callback is None:
            self.callback = lambda *x: x
        else:
            self.callback = callback

    @property
    def topic(self):
        return self._topic.strip(b'@')

    def close(self):
        self.sub.close()
        self.pub.close()
        self.node.service_clients.remove(self)
