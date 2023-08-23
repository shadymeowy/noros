import cv2
import numpy as np


class ImageMessage:
    EXTENSION = '.png'

    @staticmethod
    def deserialize(buf):
        buf = np.asarray(bytearray(buf), dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        return img

    @staticmethod
    def serialize(msg):
        buf = cv2.imencode(ImageMessage.EXTENSION, msg)[1]
        return buf.tobytes()
