from timeit import timeit
import cv2
from noros import Node, Rate
from noros.helpers.opencv import ImageMessage

node = Node()
rate = Rate(5)

take_photo = node.service_client('/camera/take_photo', ImageMessage)
take_photo.wait_for_service()

print("Calling service")
while True:
    frame = take_photo.call()
    cv2.imshow('image', frame)
    cv2.waitKey(1)
    rate.sleep()
