from math import atan2, degrees

class Location():
    """The turn angle for turning 90 degrees to the left."""
    LEFT = -90

    """The turn angle for turning 90 degrees to the right."""
    RIGHT = 90

    """The turn angle for turning 45 degrees to the left."""
    HALF_LEFT = -45

    """The turn angle for turning 45 degrees to the right."""
    HALF_RIGHT = 45

    """The turn angle for turning a full circle."""
    FULL_CIRCLE = 360

    """The turn angle for turning a full circle."""
    HALF_CIRCLE = 180

    """The turn angle for making no turn."""
    AHEAD = 0

    """COMPASS DIRECTIONS"""
    """The compass direction for north"""
    NORTH = 0

    """The compass direction for northeast"""
    NORTHEAST = 45

    """The compass direction for east"""
    EAST = 90

    """The compass direction for southeast"""
    SOUTHEAST = 135

    """The compass direction for south"""
    SOUTH = 180

    """The compass direction for southwest"""
    SOUTHWEST = 225

    """The compass direction for west"""
    WEST = 270

    """The compass direction or northwest"""
    NORTHWEST = 315

    def __init__(self, row, col):
        self.row = row
        self.col = col

    def getRow(self) -> int:
        return self.row

    def getCol(self) -> int:
        return self.col

    def getAdjacentLocation(self, direction:int):
        adjDir = (direction + self.HALF_RIGHT/2) % self.FULL_CIRCLE
        if adjDir < 0:
            adjDir += self.FULL_CIRCLE
        adjDir = int(adjDir / self.HALF_RIGHT) * self.HALF_RIGHT
        dr, dc = 0, 0
        if adjDir == self.EAST:
            dc = 1
        elif adjDir == self.SOUTHEAST:
            dc = 1
            dr = 1
        elif adjDir == self.SOUTH:
            dr = 1
        elif adjDir == self.SOUTHWEST:
            dc = -1
            dr = 1
        elif adjDir == self.WEST:
            dc = -1
        elif adjDir == self.NORTHWEST:
            dc = -1
            dr = -1
        elif adjDir == self.NORTH:
            dr = -1
        elif adjDir == self.NORTHEAST:
            dc = 1
            dr = -1
        
        return Location(self.getRow() + dr, self.getCol() + dc)
    
    def getDirectionToward(self, target) -> int:
        dx = target.getCol() - self.getCol()
        dy = target.getRow() - self.getRow()
        compassAngle = self.RIGHT - degrees(atan2(-dy, dx)) + self.HALF_RIGHT/2
        if compassAngle < 0:
            compassAngle += self.FULL_CIRCLE
        return int(compassAngle / self.HALF_RIGHT) * self.HALF_RIGHT
    
    def __hash__(self):
        return self.getRow() * 31415 + self.getCol()
        
    def __lt__(self, other):
        if not isinstance(other, Location):
            return False
        if self.getRow() == other.getRow():
            return self.getCol() < other.getCol()
        else:
            return self.getRow() < other.getRow()
    def __le__(self, other):
        if self.getRow() == other.getRow():
            return self.getCol() <= other.getCol()
        else:
            return self.getRow() < other.getRow()
    def __eq__(self, other):
        if not isinstance(other, Location):
            return False
        return (self.getRow() == other.getRow() and
                self.getCol() == other.getCol())
        
    def __ne__(self, other):
        if not isinstance(other, Location):
            return False
        return (self.getRow() != other.getRow() and
                self.getCol() != other.getCol())
        
    def __ge__(self, other):
        if self.getRow() == other.getRow():
            return self.getCol() >= other.getCol()
        else:
            return self.getRow() > other.getRow()
    def __gt__(self, other):
        if self.getRow() == other.getRow():
            return self.getCol() > other.getCol()
        else:
            return self.getRow() > other.getRow()
    
    def __str__(self):
        return "({0}, {1})".format(self.getRow(), self.getCol())
    
class Grid():
    def __init__(self):
        print("Making Grid")
        
    def getNumRows(self) -> int:
        """
        Returns the number of rows in this grid, or -1 if the grid is unbounded.
        """
        raise NotImplementedError()

    def getNumCols(self) -> int:
        """
        Returns the number of columns in this grid, or -1 if the grid is unbounded.
        """
        raise NotImplementedError()

    def isValid(self, loc:Location) -> bool:
        """
        Returns whether the provided location is valid in this grid
        """
        raise NotImplementedError()

    def put(self, loc:Location, obj):
        """
        Puts an object at a given location in this grid.
        Precondition: loc is valid within this grid.
        Returns the object previously at loc, or None if the location was
        previously unoccupied.
        """
        raise NotImplementedError()

    def remove(self, loc:Location):
        """
        Removes the object at a given location from this grid.
        Precondition: loc is valid within this grid.
        Returns the object removed from loc,
        or None if the location is unoccupied.
        """
        raise NotImplementedError()

    def get(self, loc:Location):
        """
        Returns the object at a given location in the grid.
        Precondition: loc is valid within this grid.
        Returns the object found at loc,
        or None if the location is unoccupied.
        """
        raise NotImplementedError()

    def getOccupiedLocations(self) -> tuple:
        """
        Gets the locations in this grid that contain objects.
        Returns an array list of all occupied locations in this grid
        """
        raise NotImplementedError()

    def getValidAdjacentLocations(self, loc: Location) -> list:
        raise NotImplementedError()
    
    def getEmptyAdjacentLocations(self, loc:Location) -> list:
        raise NotImplementedError()

    def getOccupiedAdjacentLocations(self, loc: Location) -> list:
        raise NotImplementedError()

    def getNeighbors(self) -> list:
        raise NotImplementedError()

class AbstractGrid(Grid):
    def __init__(self):
        print("Making AbstractGrid")
        super().__init__()
        
    def getNeighbors(self, loc:Location) -> list:
        neighbors = list()
        for neighborLoc in self.getOccupiedAdjacentLocations(loc):
            neighbors.append(self.get(neighborLoc))
        return neighbors

    def getValidAdjacentLocations(self, loc:Location) -> list:
        locs = list()
        d = Location.NORTH
        for d in range(0, Location.FULL_CIRCLE, Location.HALF_RIGHT):
            neighborLoc = loc.getAdjacentLocation(d)
            if self.isValid(neighborLoc):
                locs.append(neighborLoc)
        return locs
    
    def getEmptyAdjacentLocations(self, loc:Location) -> list:
        locs = list()
        for neighborLoc in self.getValidAdjacentLocations(loc):
            if self.get(loc) is None:
                locs.add(neighborLoc)
        return locs
    
    def __str__(self):
        output = "{"
        locs = self.getOccupiedLocations()
        if len(locs) > 0:
            for loc in locs:
                output += str(loc) + "=" + str(self.get(loc)) + ", "
            return  output[:len(output)-2]+ "}"
        else:
            return "{Empty Grid}"
        
        
    

class BoundedGrid(AbstractGrid):
    DEFAULT_ROWS = 10
    DEFAULT_COLS = 10
    def __init__(self, rows: int = None, cols: int = None):
        print("Making BoundedGrid")
        super().__init__()
        if rows is None:
            rows = self.DEFAULT_ROWS
        if cols is None:
            cols = self.DEFAULT_COLS
        if not (isinstance(rows, int) and isinstance(cols, int)):
            raise TypeError("rows and cols must be integer numbers.")
        if rows <= 0:
            raise ValueError("BoundedGrid rows must be greater than 0.")
        if cols <= 0:
            raise ValueError("BoundedGrid rows must be greater than 0.")
        self.occupantArray = [[None,]*cols,]*rows;
    
    def getNumRows(self)->int:
        return len(self.occupantArray)
    
    def getNumCols(self)->int:
        return len(self.occupantArray[0])
    
    def isValid(self, loc:Location)->bool:
        if not isinstance(loc, Location):
            raise TypeError("Loc is not a Location");
        return (0 <= loc.getRow() and
                loc.getRow() < self.getNumRows() and
                0 <= loc.getCol()and 
                loc.getCol() <self.getNumCols())
    
    def getOccupiedLocations(self)->tuple:
        # this could be optimized with an updated set of filled locations.
        locations = list()
        for row in range(self.getNumRows()):
            for col in range(self.getNumCols()):
                loc = Location(row, col)
                if self.get(loc) is not None:
                    locations.append(loc)
        return locations
    
    def get(self, loc: Location):
        if not self.isValid(loc):
            raise ValueError("Location {0} is not valid".format(str(loc)))
        return self.occupantArray[loc.getRow()][loc.getCol()]
    
    def put(self, loc:Location, obj):
        if not self.isValid(loc):
            raise ValueError("Location {0} is not valid".format(str(loc)))
        if obj is None:
            raise TypeError("Object is None-type")
        
        oldOccupant = self.get(loc)
        self.occupantArray[loc.getRow()][loc.getCol()] = obj
        return oldOccupant
    
    def remove(self, loc:Location):
        if not self.isValid(loc):
            raise ValueError("Location {0} is not valid".format(str(loc)))
        
        removedOccupant = self.get(loc)
        self.occupantArray[loc.getRow()][loc.getCol()] = None
        return removedOccupant
        

class UnboundedGrid(AbstractGrid):
    
    def __init__(self):
        print("Making UnboundedGrid")
        super().__init__()
        self.occupantMap = dict()
    
    def getNumRows(self):
        return -1
    
    def getNumCols(self):
        return -1
    
    def isValid(self, loc:Location) -> bool:
        if isinstance(loc, Location):
            return True
        raise TypeError("loc is not of type Location")
    
    def getOccupiedLocations(self):
        locations = list()
        for loc in self.occupantMap.keys():
            locations.append(loc)
        return locations
    
    def get(self, loc:Location):
        if not isinstance(loc, Location):
            raise TypeError("loc is not a Location")
        return self.occupantMap.get(loc)
    
    def put(self, loc:Location, obj):
        if not isinstance(loc, Location):
            raise TypeError("loc is not a Location")
        if obj is None:
            raise TypeError("obj is None-type")
        oldValue = self.occupantMap.get(loc)
        self.occupantMap[loc] = obj
        return oldValue
    
    def remove(self, loc:Location):
        if not isinstance(loc, Location):
            raise TypeError("loc is not a Location")
        try:
            oldValue = self.occupantMap.pop(loc)
        except KeyError:
            oldValue = None
        return oldValue
        