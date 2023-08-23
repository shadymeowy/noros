from noros import Node, Rate


node = Node()
rate = Rate(5)

pub_num = node.publisher('/number', int)

print("Publisher started")

for i in range(1000):
    pub_num.send(i)
    print("Sent:", i)
    rate.sleep()

pub_num.close()
