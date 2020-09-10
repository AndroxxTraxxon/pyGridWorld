from gridworld.actor import ActorWorld, Bug, Rock
from gridworld.grid import Location, BoundedGrid
from gridworld.colors import Color

class BoxBug(Bug):
    
    steps:int
    side_length:int
    
    def __init__(self, length:int = 4, color:Color = Color.RED):
        super().__init__()
        self.steps = 0
        self.side_length = length
        self.color = color
    
    def act(self):
        if self.steps < self.side_length and self.can_move():
            self.move()
            self.steps += 1
        else:
            self.turn()
            self.turn()
            self.steps = 0

if __name__ == "__main__":
    grid = BoundedGrid()
    world = ActorWorld(grid)
    alice = BoxBug(6)
    alice.color = Color.ORANGE
    bob = BoxBug(3)
    world.add(alice, Location(7, 8))
    world.add(bob, Location(5, 5))
    world.show()


