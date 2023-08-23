class Service:
    def __init__(self, node, topic, callback, ret_proto, protos):
        if isinstance(topic, str):
            topic = topic.encode('utf-8')
        self._topic = topic + b'@'
        self.sub = node.subscriber(
            self._topic, bytes, bytes, *protos, callback=self.handler)
        self.pub = node.publisher(self._topic, bytes, ret_proto)
        self.node = node
        self.set_callback(callback)

    def handler(self, *msgs):
        uid = msgs[0]
        self.pub.topic = self._topic + uid
        # check if this is a call or a discovery
        if len(msgs) == 1:
            self.pub.send()
            return
        muid = msgs[1]
        res = self.callback(*msgs[2:])
        if res is None:
            self.pub.send(muid)
            return
        self.pub.send(muid, res)

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
        self.node.services.remove(self)
 
