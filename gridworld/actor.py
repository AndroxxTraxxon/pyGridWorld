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
    _direction:int
    color:Color

    def __init__(self):
        self.color = Color.BLUE
        self._direction = Location.NORTH
        self.grid = None
        self.location = None

    def getGrid(self): 
        return self.grid

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, direction):
        self._direction = direction % Location.FULL_CIRCLE


    def act(self): 
        self.direction = self.direction + Location.HALF_CIRCLE

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

    @property
    def image_description(self):
        return "{name}[col:{color}; dir:{direction}]".format(
            name=self.__class__.__name__,
            color=str(self.color),
            direction=str(int(self.direction))
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
        def action():
            gr = self.grid
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
        if loc is not None:
            occupant.putSelfInGrid(self.grid, loc)
        qual_class_name = occupant.__module__ + '.' + occupant.__class__.__name__
        if qual_class_name not in self.occupant_types:
            self.occupant_types[qual_class_name] = occupant.__class__
    
    def remove(self, loc:Location) -> Actor:
        occupant:Actor = self.grid.get(loc)
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
    
    def __init__(self, color:Color=Color.RED):
        super().__init__()
        self.color = color

    def act(self):
        if self.can_move():
            self.move()
        else:
            self.turn()

    def turn(self):
        self.direction = self.direction + Location.HALF_RIGHT
    
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
        

    def can_move(self):
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
        actors = self.get_actors()
        self.process_actors(actors)
        moveLocs = self.get_move_locations()
        loc = self.select_move_location(moveLocs)
        self.make_move(loc)

    def get_actors(self) -> typing.List[Actor]:
        return list(self.grid.getNeighbors(self.location))

    def process_actors(self, actors:typing.List[Actor]):
        for a in actors:
            if not isinstance(a, [Rock, Critter]):
                a.removeSelfFromGrid()
            
    def get_move_locations(self) -> typing.List[Location]:
        return list(self.grid.getEmptyAdjacentLocations(self.location))

    def select_move_location(self, locs:typing.List[Location]) -> Location:
        n = len(locs)
        if n == 0:
            return self.location
        r = random.randrange(0, len(locs))
        return locs[r]

    def make_move(self, loc:Location):
        if loc is None:
            self.removeSelfFromGrid()
        else:
            self.moveTo(loc)