from noros import Node

node = Node()

add_two_ints = node.service_client('add_two_ints', int, int, int)
add_two_ints.wait_for_service()

while True:
    try:
        a = int(input('Enter a: '))
        b = int(input('Enter b: '))
        res = add_two_ints(a, b)
        print('Result: {}'.format(res))
    except KeyboardInterrupt:
        print('Shutting down...')
        break

add_two_ints.close()
node.close()