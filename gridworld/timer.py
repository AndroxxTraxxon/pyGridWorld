from threading import Event, Thread
from time import time, sleep
from typing import Callable

class RepeatTimerSimple(Thread):
    delay_ms:int

    def __init__(self, callback, delay_ms = 500):
        super().__init__()
        self.stopped = Event()
        self.delay_ms = delay_ms
        self.callback = callback
        self.__last_tick_time = None

    def run(self):
        self.__last_tick_time = time()
        while not self.stopped.wait(self.delay_ms/1000):
            self.callback()

    def stop(self):
        self.stopped.set()
        self.join(0.01)

class RepeatTimerBusyWait(Thread):
    
    delay_ms:int
    stopped:bool

    def __init__(self, callback:Callable[[], None], delay_ms = 500):
        super().__init__()
        self.stopped = False
        self.delay_ms = delay_ms
        self.callback = callback
        self.__last_step_time = None

    def run(self):
        self.__last_step_time = time()
        
        while not self.stopped:
            self.callback()
            ntt = self.__last_step_time + self.delay_ms/1000
            now = time()
            while(not self.stopped and (now + 0.02) < ntt):
                sleep(0.01)
                now = time()
            while ( now + 0.0005 < ntt and 
                    not self.stopped):
                now = time()
            self.__last_step_time = now

    def stop(self):
        self.stopped = True
        self.join(0.01)

RepeatTimer = RepeatTimerSimple

if __name__ == "__main__":
    pass