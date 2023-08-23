import cv2
from noros import Node
from noros.helpers.opencv import ImageMessage

node = Node()
pub_cam = node.publisher('/camera/image', ImageMessage)
video = cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

print("Publishing messages on /camera/image")
while True:
    video.grab()
    frame = video.retrieve()[1]
    pub_cam.send(frame)
