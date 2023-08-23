from time import sleep, time


class Rate:
    def __init__(self, hz):
        self.hz = hz
        self.period = 1 / hz
        self.last = time()

    def sleep(self):
        now = time()
        elapsed = now - self.last
        if elapsed < self.period:
            sleep(self.period - elapsed)
        self.last = now
