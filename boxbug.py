from gridworld.actor import ActorWorld, Bug, Rock
from gridworld.grid import Location
from gridworld.colors import Color

import pprint

class BoxBug(Bug):
    
    steps:int
    sideLength:int
    
    def __init__(self, length:int):
        super().__init__()
        self.steps = 0
        self.sideLength = length
    
    def act(self):
        if self.steps < self.sideLength and self.canMove():
            self.move()
            self.steps += 1
        else:
            self.turn()
            self.turn()
            self.steps = 0

if __name__ == "__main__":
    world = ActorWorld()
    for i in range(8):
        bug = BoxBug(i+1)
        bug.color = Color.random()
        world.add(bug)
    world.show()
    # input()

