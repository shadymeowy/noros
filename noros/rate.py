from time import sleep, time


class Rate:
    def __init__(self, hz, sleep=sleep):
        self.hz = hz
        self.period = 1 / hz
        self.last = time()
        self._sleep = sleep

    def sleep(self):
        now = time()
        elapsed = now - self.last
        if elapsed < self.period:
            self._sleep(self.period - elapsed)
        self.last = now
