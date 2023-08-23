import cv2
from noros import Node
from noros.helpers.opencv import ImageMessage

node = Node()
video = cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))


def take_photo():
    frame = video.retrieve()[1]
    return frame


sv = node.service('/camera/take_photo', take_photo, ImageMessage)

print("Waiting for service calls on /camera/take_photo")
while True:
    ret = video.grab()
    if not ret:
        break
    node.spin_once(1e-3)

sv.close()
node.close()
