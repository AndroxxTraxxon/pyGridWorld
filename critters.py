
from gridworld.actor import ActorWorld, Rock, Flower, Critter, Bug
from gridworld.grid import Location
from gridworld.colors import Color

from random import random

class CrabCritter(Critter):
    
    def __init__(self, color:Color=Color.red):
        super().__init__()
        self.color = color

    
    def get_actors(self) -> list:
        '''
        * A crab gets the actors in the three locations immediately in front, to its
        * front-right and to its front-left
        * @return a list of actors occupying these locations
        '''
        actors = list()
        dirs = (Location.AHEAD, Location.HALF_LEFT, Location.HALF_RIGHT);
        for loc in self.locations_in_dirs(dirs):
            a = self.grid.get(loc)
            if a is not None:
                actors.append(a)
        return actors

    def get_move_locations(self):
        '''
        * @return list of empty locations immediately to the right and to the left
        '''
        locs = list()
        dirs = (Location.LEFT, Location.RIGHT)
        for loc in self.locations_in_dirs(dirs):
            if self.grid.get(loc) is None:
                locs.append(loc)
        return locs

    def make_move(self, loc:Location):
        '''
        * If the crab critter doesn't move, it randomly turns left or right.
        '''
        if loc == self.location:
            r = random()
            angle = None
            if r < .5:
                angle = Location.LEFT
            else:
                angle = Location.RIGHT
            self.direction += angle
        else:
            super().make_move(loc)
    
    def locations_in_dirs(self, directions:tuple):
        '''
        * Finds the valid adjacent locations of this critter in different
        * directions.
        * @param directions - an array of directions (which are relative to the
        * current direction)
        * @return a set of valid locations that are neighbors of the current
        * location in the given directions
        '''
        for d in directions:
            neighbor = self.location.getAdjacentLocation(self.direction + d)
            if self.grid.is_valid(neighbor):
                yield neighbor


class ChameleonCritter(Critter):
    def process_actors(self, actors:list):
        '''/**
        * Randomly selects a neighbor and changes this critter's color to be the
        * same as that neighbor's. If there are no neighbors, no action is taken.
        */
        '''
        if actors:
            r = int(random() * len(actors))
            other = actors[r]
            self.color = other.color
    

    def make_move(self, loc:Location):
        '''/**
        * Turns towards the new location as it moves.
        */'''
    
        self.direction = self.location.getDirectionToward(loc)
        super().make_move(loc)
    

def run_critter():
    world = ActorWorld()
    world.add(Rock(), Location(7, 8))
    world.add(Rock(), Location(3, 3))
    world.add(Flower(Color.BLUE), Location(2, 8))
    world.add(Flower(Color.PINK), Location(5, 5))
    world.add(Flower(Color.RED), Location(1, 5))
    world.add(Flower(Color.YELLOW), Location(7, 2))
    world.add(Critter(), Location(4, 4))
    world.add(Critter(), Location(5, 8))
    world.show()

def run_crab_critter():
    world = ActorWorld()
    world.add(Rock(), Location(7, 5))
    world.add(Rock(), Location(5, 4))
    world.add(Rock(), Location(5, 7))
    world.add(Rock(), Location(7, 3))
    world.add(Flower(), Location(7, 8))
    world.add(Flower(), Location(2, 2))
    world.add(Flower(), Location(3, 5))
    world.add(Flower(), Location(3, 8))
    world.add(Bug(), Location(6, 5))
    world.add(Bug(), Location(5, 3))
    world.add(CrabCritter(), Location(4, 5))
    world.add(CrabCritter(), Location(6, 1))
    world.add(CrabCritter(), Location(7, 4))
    world.show()

def run_chameleon_critter():
    world = ActorWorld()
    world.add(Rock(), Location(7, 8))
    world.add(Rock(), Location(3, 3))
    world.add(Rock(Color.BLUE), Location(2, 8))
    world.add(Rock(Color.PINK), Location(5, 5))
    world.add(Rock(Color.RED), Location(1, 5))
    world.add(Rock(Color.YELLOW), Location(7, 2))
    world.add(ChameleonCritter(), Location(4, 4))
    world.add(ChameleonCritter(), Location(5, 8))
    world.show()


run_type = "crab"
if __name__ == "__main__":
    # run_critter()
    run_crab_critter()