from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GPS(_message.Message):
    __slots__ = ["timestamp", "latitude", "longitude"]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    timestamp: float
    latitude: float
    longitude: float
    def __init__(self, timestamp: _Optional[float] = ..., latitude: _Optional[float] = ..., longitude: _Optional[float] = ...) -> None: ...
