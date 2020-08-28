import pyGridWorld.colors as colors
from pyGridWorld.grid import Grid, Location
import pyGridWorld.world as world
import typing

import random
import tkinter as tk



class Actor:

    grid:Grid
    location:Location
    direction:int
    color:colors.Color

    def __init__(self):
        self.color = colors.BLUE
        self.direction = Location.NORTH
        self.grid = None
        self.location = None

    def getGrid(self): 
        return self.grid

    def act(self): 
        self.direction += Location.HALF_CIRCLE

    def putSelfInGrid(self, gr:Grid, loc:Location):
        if gr is not None:
            raise ValueError("This actor is already contained in a grid.")
        actor:Actor = gr.get(loc)
        if actor is not None:
            actor.removeSelfFromGrid()
        gr.put(loc, self)
        self.grid = gr
        self.location = loc

    def removeSelfFromGrid(self):
        if self.grid is None:
            raise ValueError("This actor is not contained in a grid")
        if self.grid.get(self.location) is not self:
            raise ValueError(
                "The grid contains a different actor at location " + 
                str(self.location) + "."
            )
        self.grid.remove(self.location)
        self.grid = None
        self.location = None

    def moveTo(self, loc:Location):
        if self.grid is None:
            raise ValueError("This actor is not in a grid.")
        if self.grid.get(self.location) is not self:
            raise ValueError(
                "The grid contains a different actor at location " + 
                str(self.location) + "."
            )
        if not self.grid.isValid(loc):
            raise ValueError("Location" + str(loc) + "is not valid.")

        if loc == self.location:
            return
        self.grid.remove(self.location)
        other:Actor = self.grid.get(loc)
        if other is not None:
            other.removeSelfFromGrid()
        self.location = loc
        self.grid.put(self.location, self)

    def __str__(self):
        return (
            self.__class__.__name__ + 
            "[location=" + self.location + 
            ",direction=" + self.direction + 
            ",color=" + self.color + "]"
        )


class ActorWorld(world.World):
    DEFAULT_MESSAGE = "Click on a grid location to construct or manipulate an actor."

    def __init__(self, gr:Grid):
        super(gr)

    def show(self):
        if(self.message is None):
            self.setMessage(self.DEFAULT_MESSAGE)
        super.show()
    
    def step(self):
        gr = self.getGrid()
        actors:typing.List[Actor] = list()
        for loc in gr.occupiedLocations:
            actors.append(gr.get(loc))
        for a in actors:
            if a.grid == gr:
                a.act()
    
    def add(self, occupant:Actor, loc:Location = None):
        if loc is None:
            loc = self.getRandomEmptyLocation()
        if loc is not None:
            occupant.putSelfInGrid(self.getGrid(), loc)
    
    def remove(self, loc:Location) -> Actor:
        occupant:Actor = self.getGrid().get(loc)
        if occupant is not None:
            occupant.removeSelfFromGrid()
        return occupant
    

class Flower(Actor):
    DARKENING_FACTOR = 0.05

    def __init__(self, color=colors.PINK):
        super().__init__()
        self.color = color

    def act(self):
        red = int(self.color.red * (1-self.DARKENING_FACTOR))
        green = int(self.color.green * (1-self.DARKENING_FACTOR))
        blue = int(self.color.blue * (1-self.DARKENING_FACTOR))
        self.color = colors.Color(red, green, blue)
        

class Bug(Actor):
    
    def __init__(self, color=colors.RED):
        super().__init__()
        self.color = color

    def act(self):
        if self.canMove():
            self.move()
        else:
            self.turn()

    def turn(self):
        self.direction += Location.HALF_RIGHT
    
    def move(self):
        if self.grid is None:
            return
        loc = self.location
        nextLoc = loc.getAdjacentLocation(self.direction)
        if self.grid.isValid(nextLoc):
            self.moveTo(nextLoc)
        else:
            self.removeSelfFromGrid()
        flower = Flower(self.color)
        flower.putSelfInGrid(self.grid, loc)
        

    def canMove(self):
        if self.grid is None:
            return False
        loc = self.location
        nextLoc = loc.getAdjacentLocation(self.direction)
        if not self.grid.isValid(nextLoc):
            return False
        neighbor = self.grid.get(nextLoc)
        return neighbor is None or isinstance(neighbor, Flower)


class Rock(Actor):

    def __init__(self, color=colors.BLACK):
        super().__init__()
        self.color = color

    def act(self):
        pass

class Critter(Actor):

    def act(self):
        if self.grid is None:
            return
        actors = self.getActors()
        self.processActors(actors)
        moveLocs = self.getMoveLocations()
        loc = self.selectMoveLocation(moveLocs)
        self.makeMove(loc)

    def getActors(self) -> typing.List[Actor]:
        return self.grid.getNeighbors(self.location)

    def processActors(self, actors:typing.List[Actor]):
        for a in actors:
            if not isinstance(a, [Rock, Critter]):
                a.removeSelfFromGrid()
            
    def getMoveLocations(self) -> typing.List[Location]:
        return self.grid.getEmptyAdjacentLocations(self.location)

    def selectMoveLocation(self, locs:typing.List[Location]) -> Location:
        n = len(locs)
        if n == 0:
            return self.location
        r = random.randrange(0, len(locs))
        return locs[r]

    def makeMove(self, loc:Location):
        if loc is None:
            self.removeSelfFromGrid()
        else:
            self.moveTo(loc)