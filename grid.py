import typing 
import math


class Location:

    row: int
    col: int

    LEFT:int = -90
    RIGHT:int = 90
    HALF_LEFT:int = -45
    HALF_RIGHT:int = 45
    FULL_CIRCLE:int = 360
    HALF_CIRCLE:int = 180
    AHEAD:int = 0

    NORTH:int = 0
    NORTHEAST:int = 45
    EAST:int = 90
    SOUTHEAST:int = 135
    SOUTH:int = 180
    SOUTHWEST:int = 225
    WEST:int = 270
    NORTHWEST:int = 315

    def __init__(self, r:int, c:int):
        self.row = r
        self.col = c

    def getAdjacentLocation(self, direction:int) -> "Location":
        adjustedDirection:int = (direction + self.HALF_RIGHT // 2) % self.FULL_CIRCLE
        if adjustedDirection < 0:
            adjustedDirection += self.FULL_CIRCLE

        adjustedDirection = (adjustedDirection // self.HALF_RIGHT) * self.HALF_RIGHT
        dc, dr = {
            self.EAST: (1, 0),
            self.SOUTHEAST: (1, 1),
            self.SOUTH: (0, 1),
            self.SOUTHWEST: (-1, 1),
            self.WEST: (-1, 0),
            self.NORTHWEST: (-1, -1),
            self.NORTH: (0, -1),
            self.NORTHEAST: (1, -1)
        }[adjustedDirection]
        
        return self.__class__(self.row + dr, self.col + dc)

    def getDirectionToward(self, target:"Location") -> int:
        dx = target.col - self.col
        dy = target.row - self.row
        angle = int(math.degrees(math.atan2(-dy, dx)))
        compassAngle = self.RIGHT - angle

        compassAngle += self.HALF_RIGHT // 2

        if(compassAngle < 0):
            compassAngle += self.FULL_CIRCLE
        
        return (compassAngle // self.HALF_RIGHT) * self.HALF_RIGHT

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.row == other.row and self.col == other.col

    def __hash__(self) -> int:
        return self.row * 3737 + self.col

    def compareTo(self, other) -> int:
        if self.row < other.row: return -1
        if self.row > other.row: return 1
        if self.col < other.col: return -1
        if self.col > other.col: return 1
        return 0

    def __str__(self) -> str:
        return "(" + str(self.row) + ", " + str(self.col) + ")"
        

class Grid:

    @property
    def rowCount(self) -> int:
        raise NotImplementedError()

    @property
    def colCount(self) -> int:
        raise NotImplementedError()

    def isValid(self, loc:Location) -> bool:
        raise NotImplementedError()

    def put(self, loc:Location, obj):
        raise NotImplementedError()

    def remove(self, loc:Location):
        raise NotImplementedError()

    def get(self, loc:Location):
        raise NotImplementedError()

    @property
    def occupiedLocations(self) -> typing.List[Location]:
        raise NotImplementedError()

    def getValidAdjacentLocations(self, loc:Location):
        raise NotImplementedError()

    def getEmptyAdjacentLocations(self, loc:Location):
        raise NotImplementedError()

    def getOccupiedAdjacentLocations(self, loc:Location):
        raise NotImplementedError()

    def getNeighbors(self, loc:Location):
        raise NotImplementedError


class AbstractGrid(Grid):

    def getNeighbors(self, loc:Location) -> list:
        neighbors = list()
        for neighborLoc in self.getOccupiedAdjacentLocations(loc):
            neighbors.append(self.get(neighborLoc))
        return neighbors

    def getValidAdjacentLocations(self, loc:Location) -> typing.List[Location]:
        locs = list()
        for d in range(Location.NORTH, Location.FULL_CIRCLE, Location.HALF_RIGHT):
            neighborLoc = loc.getAdjacentLocation(d)
            if(self.isValid(neighborLoc)):
                locs.append(neighborLoc)
        return locs

    def getEmptyAdjacentLocations(self, loc:Location) -> typing.List[Location]:
        locs = list()
        for neighborLoc in self.getValidAdjacentLocations(loc):
            if self.get(neighborLoc) is None:
                locs.append(neighborLoc)
        return locs

    def getOccupiedAdjacentLocations(self, loc:Location) -> typing.List[Location]:
        locs = list()
        for neighborLoc in self.getValidAdjacentLocations(loc):
            if self.get(neighborLoc) is not None:
                locs.append(neighborLoc)
        return locs

    def __str__(self):
        return self.__class__.__name__ + "{" + ", ".join(map(
            (lambda x: str(x) + "=" + str(self.get(x))), 
            self.occupiedLocations
        )) + "}"


class BoundedGrid(AbstractGrid):
    occupant_array: typing.List[list]

    def __init__(self, rows:int, cols:int):
        if rows <= 0:
            raise ValueError("rows <= 0")
        if cols <= 0:
            raise ValueError("cols <= 0")
        self.occupant_array = [[None] * cols] * rows

    @property
    def rowCount(self):
        return len(self.occupant_array)

    @property
    def colCount(self):
        return len(self.occupant_array[0])

    def isValid(self, loc:Location):
        return (
            0 <= loc.row and
            loc.row < self.rowCount and
            0 <= loc.col and 
            loc.col < self.colCount
        )
    
    @property
    def occupiedLocations(self):
        the_locations = list()
        for r, row in enumerate(self.occupant_array):
            for c, item in enumerate(row):
                if item is not None:
                    the_locations.append(Location(r,c))
        return the_locations

    def get(self, loc:Location):
        if not self.isValid(loc):
            raise ValueError("Location" + str(loc) + "is not valid")
        return self.occupant_array[loc.row][loc.col]

    def put(self, loc:Location, obj):
        if not self.isValid(loc):
            raise ValueError("Location" + str(loc) + "is not valid")
        if obj is None:
            raise ValueError("obj is None")
        old_occupant = self.get(loc)
        self.occupant_array[loc.row][loc.col] = obj
        return old_occupant

    def remove(self, loc:Location):
        if not self.isValid(loc):
            raise ValueError("Location" + str(loc) + "is not valid")
        old_occupant = self.get(loc)
        self.occupant_array[loc.row][loc.col] = None
        return old_occupant


class UnboundedGrid(AbstractGrid):

    occupant_map:dict

    def __init__(self):
        self.occupant_map = dict()

    @property
    def rowCount(self) -> int:
        return -1

    @property
    def colCount(self) -> int:
        return -1

    def isValid(self, loc:Location) -> bool:
        return True

    def occupiedLocations(self) -> typing.List[Location]:
        return list(self.occupant_map.keys())
    
    def get(self, loc:Location):
        if loc is None:
            raise ValueError("loc is None")
        return self.occupant_map.get(loc)
    
    def put(self, loc:Location, obj):
        if loc is None:
            raise ValueError("loc is None")
        if obj is None:
            raise ValueError("obj is None")
        old_occupant = self.occupant_map.get(loc)
        self.occupant_map[loc] = obj
        return old_occupant

    def remove(self, loc:Location):
        if loc is None:
            raise ValueError("loc is None")
        old_occupant = self.occupant_map.get(loc)
        self.occupant_map[loc] = None
        return old_occupant