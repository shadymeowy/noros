from noros import Node

node = Node()


def cb_num(num):
    print("Received:", num)


sub_position = node.subscriber('/number', int, callback=cb_num)

print("Subscriber started")
node.spin()

sub_position.close()