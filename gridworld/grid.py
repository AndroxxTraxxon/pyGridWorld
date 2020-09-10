import typing 
import math
import tkinter as tk


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
    
    def __repr__(self) -> str:
        return self.__class__.__name__ + str(self)
        

class Grid:

    @property
    def row_count(self) -> int:
        raise NotImplementedError()

    @property
    def col_count(self) -> int:
        raise NotImplementedError()

    def is_valid(self, loc:Location) -> bool:
        raise NotImplementedError()

    def put(self, loc:Location, obj):
        raise NotImplementedError()

    def remove(self, loc:Location):
        raise NotImplementedError()

    def get(self, loc:Location):
        raise NotImplementedError()

    @property
    def occupied_locations(self) -> typing.List[Location]:
        raise NotImplementedError()

    def valid_adjacent_locations(self, loc:Location):
        raise NotImplementedError()

    def empty_adjacent_locations(self, loc:Location):
        raise NotImplementedError()

    def occupied_adjacent_locations(self, loc:Location):
        raise NotImplementedError()

    def neighbors(self, loc:Location):
        raise NotImplementedError()

    @classmethod
    def builder(cls, parent: tk.Toplevel):
        raise NotImplementedError()


class AbstractGrid(Grid):

    def neighbors(self, loc:Location) -> typing.Iterable:
        for neighborLoc in self.occupied_adjacent_locations(loc):
            yield self.get(neighborLoc)

    def valid_adjacent_locations(self, loc:Location) -> typing.Iterable[Location]:
        for d in range(Location.NORTH, Location.FULL_CIRCLE, Location.HALF_RIGHT):
            neighborLoc = loc.getAdjacentLocation(d)
            if(self.is_valid(neighborLoc)):
                yield neighborLoc

    def empty_adjacent_locations(self, loc:Location) -> typing.Iterable[Location]:
        for neighborLoc in self.valid_adjacent_locations(loc):
            if self.get(neighborLoc) is None:
                yield neighborLoc

    def occupied_adjacent_locations(self, loc:Location) -> typing.Iterable[Location]:
        for neighborLoc in self.valid_adjacent_locations(loc):
            if self.get(neighborLoc) is not None:
                yield neighborLoc

    def __str__(self):
        return "{name}({rows}x{cols}){{{occupants}}}".format(
            name=self.__class__.__name__,
            rows=self.row_count,
            cols=self.col_count,
            occupants = ", ".join(
                map(
                    lambda x: str(x) + "=" + str(self.get(x)), 
                    list(self.occupied_locations)
                )
            )
        )


class BoundedGrid(AbstractGrid):
    occupant_array: typing.List[list]

    def __init__(self, rows:int=10, cols:int=10):
        if rows <= 0:
            raise ValueError("rows <= 0")
        if cols <= 0:
            raise ValueError("cols <= 0")
        self.occupant_array = [[None for c in range(cols)] for r in range(rows)]

    @property
    def row_count(self):
        return len(self.occupant_array)

    @property
    def col_count(self):
        return len(self.occupant_array[0])

    def is_valid(self, loc:Location):
        return (
            0 <= loc.row and
            loc.row < self.row_count and
            0 <= loc.col and 
            loc.col < self.col_count
        )
    
    @property
    def occupied_locations(self):
        for r, row in enumerate(self.occupant_array):
            for c, item in enumerate(row):
                if item is not None:
                    yield Location(r,c)

    def get(self, loc:Location):
        if not self.is_valid(loc):
            raise ValueError("Location" + str(loc) + "is not valid")
        return self.occupant_array[loc.row][loc.col]

    def put(self, loc:Location, obj):
        if not self.is_valid(loc):
            raise ValueError("Location" + str(loc) + "is not valid")
        if obj is None:
            raise ValueError("obj is None")
        old_occupant = self.get(loc)
        self.occupant_array[loc.row][loc.col] = obj
        return old_occupant

    def remove(self, loc:Location):
        if not self.is_valid(loc):
            raise ValueError("Location" + str(loc) + "is not valid")
        old_occupant = self.get(loc)
        self.occupant_array[loc.row][loc.col] = None
        return old_occupant

class UnboundedGrid(AbstractGrid):

    occupant_map:dict

    def __init__(self):
        self.occupant_map = dict()

    @property
    def row_count(self) -> int:
        return -1

    @property
    def col_count(self) -> int:
        return -1

    def is_valid(self, loc:Location) -> bool:
        return True

    @property
    def occupied_locations(self) -> typing.List[Location]:
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
