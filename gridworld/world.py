from gridworld.grid import Location, Grid, BoundedGrid, UnboundedGrid
import random
import tkinter as tk


class World:
    _grid: Grid = None
    occupant_types: dict = None
    grid_types: dict = None
    message: str = None
    frame = None

    generator:random.Random = random.Random()

    DEFAULT_ROWS = 10
    DEFAULT_COLS = 10

    def __init__(self, g:Grid=None):
        if g is None:
            g = BoundedGrid(self.DEFAULT_ROWS, self.DEFAULT_COLS)
        self.grid = g
        self.grid_types = dict()
        self.occupant_types = dict()
        self.add_grid_type(BoundedGrid)
        self.add_grid_type(UnboundedGrid)

    def show(self):
        if self.frame is None:
            from gridworld.gui import WorldFrame
            self.frame = WorldFrame(self)
        self.frame.show()
        
    @property
    def grid(self):
        return self._grid

    @grid.setter
    def grid(self, newGrid:Grid):
        self._grid = newGrid
        self.repaint()

    def add_grid_type(self, grid_type:type):
        qual_class_name = grid_type.__module__ + '.' + grid_type.__class__.__name__
        self.grid_types[qual_class_name] = grid_type

    def setMessage(self, newMessage:str):
        self.message = newMessage
        self.repaint()
    
    def getMessage(self):
        return self.message

    def step(self):
        self.repaint()
    
    def locationClicked(self, loc:Location) -> bool:
        return False

    def keyPressed(self, desc:str, loc:Location) -> bool:
        return False

    def getRandomEmptyLocation(self) -> Location:
        gr = self.grid()
        rows = gr.rowCount
        cols = gr.colCount
        if rows > 0 and cols > 0: # bounded grid
            emptyLocs = list()
            for r, row in enumerate(gr.occupant_array):
                for c, item in enumerate(row):
                    if item is None:
                        emptyLocs.append(Location(r,c))
            if(len(emptyLocs) == 0):
                return None
            r = int(self.generator.random() * len(emptyLocs))
            return emptyLocs[r]
        else:
            while True:
                r = None
                if rows < 0:
                    r = int(self.DEFAULT_ROWS * self.generator.gauss(0, 1.0))
                else:
                    r = self.generator.randint(0, rows)
                c = None
                if rows < 0:
                    c = int(self.DEFAULT_COLS * self.generator.gauss(0, 1.0))
                else:
                    c = self.generator.randint(0, cols)
                loc = Location(r,c)
                if(gr.isValid(loc) and gr.get(loc) is None):
                    return loc

    def add(self, occupant, loc:Location):
        self.grid().put(loc, occupant)
        qual_class_name = occupant.__module__ + '.' + occupant.__class__.__name__
        if qual_class_name not in self.occupant_types:
            self.occupant_types[qual_class_name] = occupant.__class__
        self.repaint()

    def remove(self, loc:Location):
        r = self.grid().remove(loc)
        self.repaint()
        return r

    def repaint(self): 
        if self.frame != None:
            self.frame.rerender()

    def __str__(self):
        s = "World:\n"
        gr = self.grid()
        rmin = 0
        rmax = gr.rowCount
        cmin = 0
        cmax = gr.colCount
        if rmax < 0 or cmax < 0:
            for loc in gr.occupiedLocations:
                r = loc.row
                c = loc.col
                if r < rmin:
                    rmin = r
                if r > rmax:
                    rmax = r
                if c < cmin:
                    cmin = c
                if c > cmax:
                    cmax = c

        s += "#" * (cmax-cmin) + "\n"
        for i in range(rmin, rmax):
            for j in range(cmin, cmax):
                obj = gr.get(Location(i,j))
                if obj is None:
                    s += " "
                else:
                    s += str(obj)[0]
            s += "\n"
        s += "#" * (cmax-cmin)
        return s


    

    




                            




        
