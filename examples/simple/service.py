from noros import Node

node = Node()


def add_two_ints(a, b):
    print('Adding {} + {}'.format(a, b))
    return a + b


sv = node.service('add_two_ints', add_two_ints, int, int, int)

node.spin()

sv.close()
node.close()
