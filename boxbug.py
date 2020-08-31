from gridworld.actor import ActorWorld, Bug, Rock
from gridworld.grid import Location
from gridworld.colors import Color
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
    alice = Bug(Color.ORANGE)

    bob = BoxBug(3)


    world.add(alice, Location(7,8))
    world.add(bob, Location(5,5))
    world.add(Rock(), Location(4, 9))
    world.show()
    # input()

