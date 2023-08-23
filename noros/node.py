import zmq
from .publisher import Publisher
from .subscriber import Subscriber
from .service import Service
from .service_client import ServiceClient


class Node:
    def __init__(self, context=None, sub_conn="ipc:///tmp/sub", pub_conn="ipc:///tmp/pub"):
        if context is None:
            context = zmq.Context()
        self.context = context
        self.sub_conn = sub_conn
        self.pub_conn = pub_conn
        self.pubs = []
        self.subs = []
        self.services = []
        self.service_clients = []
        self._ext_polls = []
        self._shutdown = False

        self.construct_poller()

    def publisher(self, topic, *protos, callback=None):
        socket = self.pub_socket()
        pub = Publisher(socket, self, topic, callback, protos)
        self.pubs.append(pub)
        return pub

    def subscriber(self, topic, *protos, callback=None):
        socket = self.sub_socket()
        sub = Subscriber(socket, self, topic, callback, protos)
        self.subs.append(sub)
        self.construct_poller()
        return sub

    def service(self, topic, fn, ret_proto, *protos):
        service = Service(self, topic, fn, ret_proto, protos)
        self.services.append(service)
        return service

    def service_client(self, topic, ret_proto, *protos, callback=None):
        service_client = ServiceClient(
            self, topic, callback, ret_proto, protos)
        self.service_clients.append(service_client)
        return service_client

    def pub_socket(self):
        socket = self.context.socket(zmq.PUB)
        socket.connect(self.pub_conn)
        return socket

    def sub_socket(self):
        socket = self.context.socket(zmq.SUB)
        socket.connect(self.sub_conn)
        return socket

    def add_ext_socket(self, sock, callback):
        self._ext_polls.append((sock, callback))
        self.construct_poller()

    def remove_ext_sub(self, sock):
        for s, cb in self._ext_polls:
            if s == sock:
                self._ext_polls.remove((s, cb))
                self.construct_poller()
                return

    def construct_poller(self):
        poller = zmq.Poller()
        for sub in self.subs:
            poller.register(sub.socket, zmq.POLLIN)
        for socket, _ in self._ext_polls:
            poller.register(socket, zmq.POLLIN)
        self.poller = poller

    def spin_once(self, timeout=None):
        socks = dict(self.poller.poll(timeout=timeout))
        for sub in self.subs:
            if sub.socket in socks and socks[sub.socket] == zmq.POLLIN:
                try:
                    sub.recv(zmq.NOBLOCK)
                except zmq.Again:
                    pass
        for socket, callback in self._ext_polls:
            if socket in socks:
                callback(socket)

    def spin(self):
        while not self._shutdown:
            self.spin_once()

    def close(self):
        # self.context.term()
        self._shutdown = True

    def shutdown(self):
        self._shutdown = True

    @property
    def is_shutdown(self):
        return self._shutdown
