import cv2
from noros import Node
from noros.helpers.opencv import ImageMessage

node = Node()


def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(1)


sub_cam = node.subscriber('/camera/image', ImageMessage)
sub_cam.callback = show_image

node.spin()
