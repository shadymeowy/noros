def serializer(typ):
    if hasattr(typ, 'SerializeToString'):
        return lambda x: x.SerializeToString()
    elif hasattr(typ, 'pack'):
        return lambda x: x.pack()
    elif typ is bytes:
        return lambda x: x
    elif typ is str:
        return lambda x: x.encode('utf-8')
    elif typ is int:
        return lambda x: x.to_bytes(8, 'little')
    elif typ is float:
        return lambda x: x.to_bytes(8, 'little')
    elif typ is bool:
        return lambda x: b'\x01' if x else b'\x00'
    else:
        return typ


def deserializer(typ):
    if hasattr(typ, 'ParseFromString'):
        return ProtoConstructor(typ)
    elif hasattr(typ, 'unpack'):
        return typ.unpack
    elif typ is bytes:
        return lambda x: x
    elif typ is str:
        return lambda x: x.decode('utf-8')
    elif typ is int:
        return lambda x: int.from_bytes(x, 'little')
    elif typ is float:
        return lambda x: float.from_bytes(x, 'little')
    elif typ is bool:
        return lambda x: x == b'\x01'
    else:
        return typ


class ProtoConstructor:
    def __init__(self, proto):
        self.proto = proto

    def __call__(self, byts):
        msg = self.proto()
        msg.ParseFromString(byts)
        return msg
