from gridworld.colors import Color
from gridworld.grid import Grid, Location
from gridworld.world import World
from threading import Thread
import typing

import random
import tkinter as tk


class Actor:

    grid:Grid
    location:Location
    direction:int
    color:Color

    def __init__(self):
        self.color = Color.BLUE
        self.direction = Location.NORTH
        self.grid = None
        self.location = None

    def getGrid(self): 
        return self.grid

    def act(self): 
        self.direction += Location.HALF_CIRCLE

    def putSelfInGrid(self, gr:Grid, loc:Location):
        if self.grid is not None:
            raise ValueError("This actor is already contained in a grid.")
        if gr is None:
            raise ValueError("grid is None")
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
            "[location=" + str(self.location) + 
            ",direction=" + str(self.direction) + 
            ",color=" + str(self.color) + "]"
        )


class ActorWorld(World):
    DEFAULT_MESSAGE = "Click on a grid location to construct or manipulate an actor."

    def __init__(self, gr:Grid = None):
        super().__init__(gr)
        self.step_thread:Thread = None

    def show(self):
        if(self.message is None):
            self.setMessage(self.DEFAULT_MESSAGE)
        super().show()
    
    def step(self):
        if self.step_thread is not None and self.step_thread.is_alive:
            self.step_thread.join(0.01)
        def action():
            gr = self.getGrid()
            actors:typing.List[Actor] = list()
            for loc in gr.occupiedLocations:
                actors.append(gr.get(loc))
            for a in actors:
                if a.grid == gr:
                    a.act()
            self.repaint()
        self.step_thread = Thread(target=action)
        self.step_thread.start() 
    
    def add(self, occupant:Actor, loc:Location = None):
        if loc is None:
            loc = self.getRandomEmptyLocation()
            print(loc)
        if loc is not None:
            occupant.putSelfInGrid(self.getGrid(), loc)
        qual_class_name = occupant.__module__ + '.' + occupant.__class__.__name__
        if qual_class_name not in self.occupant_types:
            self.occupant_types[qual_class_name] = occupant.__class__
    
    def remove(self, loc:Location) -> Actor:
        occupant:Actor = self.getGrid().get(loc)
        if occupant is not None:
            occupant.removeSelfFromGrid()
        return occupant
    

class Flower(Actor):
    DARKENING_FACTOR = 0.05

    def __init__(self, color=Color.PINK):
        super().__init__()
        self.color = color

    def act(self):
        red = int(self.color.red * (1-self.DARKENING_FACTOR))
        green = int(self.color.green * (1-self.DARKENING_FACTOR))
        blue = int(self.color.blue * (1-self.DARKENING_FACTOR))
        self.color = Color(red, green, blue)
        

class Bug(Actor):
    
    def __init__(self, color=Color.RED):
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

    def __init__(self, color=Color.BLACK):
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