from grid import Grid, Location
import world
from PyQt5.Qt import QColor as Color
from PyQt5.Qt import qApp
from random import randint

class Actor():
    DEFAULT_COLOR = 'blue'
    def __init__(self, imagePath = None):
        self.color = Color('blue')
        self.direction = Location.NORTH
        self.grid = None
        self.location = None
        if imagePath is None:
            self.imagePath = str(self.__class__.__name__) + ".gif"
        
    def getColor(self) -> Color:
        return self.color
    
    def setColor(self, color: Color = None):
        if isinstance(color, Color):
            self.color = color
        elif isinstance(color, str) and color in Color.colorNames():
            self.color = Color(color)
        elif color is None:
            self.color = Color(self.DEFAULT_COLOR)
        else:
            raise ValueError("Unknown Color Value: " + str(color))
        
    def resetColor(self):
        self.setColor()
        
    def getDirection(self) -> int:
        return self.direction
    
    def setDirection(self, newDirection: int):
        self.direction = int(newDirection) % Location.FULL_CIRCLE
        if self.direction < 0:
            self.direction += Location.FULL_CIRCLE
        
    def getGrid(self) -> Grid:
        return self.grid
    
    def getLocation(self) -> Location:
        return self.location
    
    def putSelfInGrid(self, grid:Grid, loc:Location):
        assert self.grid is None, "This Actor is already contained in a grid."
        if not isinstance(grid, Grid):
            raise TypeError("grid is not a Grid")
        actor = grid.get(loc)
        if actor is not None:
            actor.removeSelfFromGrid()
        grid.put(loc, self)
        self.grid = grid
        self.location = loc
        return actor
        
    def removeSelfFromGrid(self):
        assert self.grid is not None, "This Actor is not contained in a grid."
        assert self is self.grid.get(self.location), "This grid contains a different actor at location {0}.".format(str(self.location))
        self.grid.remove(self.location)
        self.grid = None
        self.location = None
        
    def moveTo(self, newLocation:Location):
        assert self.grid is not None, "This actor is not in a grid."
        assert self is self.grid.get(self.location), "This grid contains a different actor at location {0}.".format(str(self.location))
        if not self.grid.isValid(newLocation):
            raise ValueError("Location {0} is not valid in this grid.".format(str(newLocation)))
        if newLocation == self.location:
            return 
        self.grid.remove(self.location)
        other = self.grid.get(newLocation)
        if other is not None:
            other.removeSelfFromGrid()
        self.location = newLocation
        self.grid.put(self.location, self)
    
    def act(self):
        self.setDirection(self.direction + Location.HALF_CIRCLE)
        
    def __str__(self):
        return "{0}[location={1},direction={2},color={3}]".format(self.__class__.__name__, str(self.location), str(self.direction), str(self.color))

class ActorWorld(world.World):
    
    DEFAULT_MESSAGE = "Click on a grid location to construct or manipulate an actor."
    
    def __init__(self, grid:Grid = None):
        print("Making ActorWorld")
        super().__init__(g = grid)
            
    def show(self):
        print()
        if(self.getMessage() is None):
            self.setMessage(self.DEFAULT_MESSAGE)
        super().show();
    def step(self):
        gr = self.getGrid()
        actors = list()
        for loc in gr.getOccupiedLocations():
            actors.append(gr.get(loc))
            
        for a in actors:
            if a.getGrid() is gr:
                a.act()
                
    def add(self, occupant:Actor, loc:Location = None):
        if loc is None:
            return occupant.putSelfInGrid(self.getGrid(), self.getRandomEmptyLocation())
        else:
            return occupant.putSelfInGrid(self.getGrid(), loc)
        
    def remove(self, loc:Location):
        occupant = self.getGrid().get(loc)
        if occupant is None:
            return None
        occupant.removeSelfFromGrid()
        return occupant

class Bug(Actor):
    DEFAULT_COLOR = 'red'
    def __init__(self, bugColor:Color = None, imagePath = None):
        super().__init__(imagePath = imagePath)
        self.setColor(bugColor)
    
    def act(self):
        if self.canMove():
            self.move()
        else:
            self.turn()
            
    def turn(self):
        self.setDirection(self.getDirection() + Location.HALF_RIGHT)
        
    def move(self):
        gr = self.getGrid()
        if gr is None:
            return
        loc = self.getLocation()
        nextLoc = loc.getAdjacentLocation(self.getDirection())
        if gr.isValid(nextLoc):
            self.moveTo(nextLoc)
        else:
            self.removeSelfFromGrid()
        
        flower = Flower(self.getColor())
        flower.putSelfInGrid(gr, loc)
        
    def canMove(self):
        gr = self.getGrid()
        if gr is None:
            return False
        loc = self.getLocation()
        nextLoc = loc.getAdjacentLocation(self.getDirection())
        if not gr.isValid(nextLoc):
            return False
        neighbor = gr.get(nextLoc)
        return (neighbor is None or isinstance(neighbor, Flower))

class Critter(Actor):
    DEFAULT_COLOR = 'brown'
    def __init__(self, critterColor = None,imagePath = None):
        super().__init__(imagePath = imagePath)
        self.setColor(critterColor)
        
    def act(self):
        if self.getGrid() is None:
            return
        actors = self.getActors()
        self.processActors(actors)
        moveLocs = self.getMoveLocations()
        nextLoc = self.selectMoveLocation(moveLocs)
        self.makeMove(nextLoc)
        
    def getActors(self):
        return self.getGrid().getNeighbors(self.location)
    
    def processActors(self, actors:list):
        for a in actors:
            if not isinstance(a, Rock) and not isinstance(a, Critter):
                a.removeSelfFromGrid()
                
    def getMoveLocations(self):
        return self.getGrid().getEmptyAdjacentLocations(self.getLocation())
        
    def selectMoveLocation(self, locs:list) -> Location:
        n = len(locs)
        if n == 0:
            return self.getLocation()
        r = randint(0, len(locs)-1)
        return locs[r]
    
    def makeMove(self, loc:Location):
        if loc is None:
            self.removeSelfFromGrid()
        else:
            self.moveTo(loc)

class Flower(Actor):
    DEFAULT_COLOR = 'pink'
    def __init__(self, flowerColor:Color = None, imagePath = None):
        super().__init__(imagePath = imagePath)
        if flowerColor is None:
            flowerColor = Color
        self.setColor(flowerColor)
        
    def act(self):
        c = self.getColor()
        red, green, blue, alpha = c.getRgb()
        red *=(1-self.DARKENING_FACTOR)
        green *=(1-self.DARKENING_FACTOR)
        blue *=(1-self.DARKENING_FACTOR)
        self.setColor(Color(red, green, blue, alpha))
class Rock(Actor):
    DEFAULT_COLOR = 'black'
    def __init__(self, rockColor:Color = None, imagePath = None):
        super().__init__(imagePath = imagePath)
        
        self.setColor(rockColor)
    
    def act(self):
        return