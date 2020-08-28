import pyGridWorld.grid as grid
import pyGridWorld.gui as gui
import random
import tkinter as tk


class World:
    gr: grid.Grid = None
    occupantClassNames: set = None
    gridClassNames: set = None
    message: str = None
    frame: tk.Frame = None

    generator:random.Random = random.Random()

    DEFAULT_ROWS = 10
    DEFAULT_COLS = 10

    def __init__(self, g:grid.Grid = grid.BoundedGrid(DEFAULT_ROWS, DEFAULT_COLS)):
        self.gr = g
        self.gridClassNames = set()
        self.occupantClassNames = set()
        self.gridClassNames.add(grid.BoundedGrid.__name__)
        self.gridClassNames.add(grid.UnboundedGrid.__name__)
        print(self.gridClassNames)

    def show(self):
        if self.frame is None:
            self.frame = gui.WorldFrame(self)
            # self.frame.setVisible(True)
        # else:
            # self.frame.repaint()

    def getGrid(self):
        return self.gr

    def setGrid(self, newGrid:grid.Grid):
        self.gr = newGrid
        self.repaint()

    def setMessage(self, newMessage:str):
        self.message = newMessage
        self.repaint()
    
    def getMessage(self):
        return self.message

    def step(self):
        self.repaint()
    
    def locationClicked(self, loc:grid.Location) -> bool:
        return False

    def keyPressed(self, desc:str, loc:grid.Location) -> bool:
        return False

    def getRandomEmptyLocation(self) -> grid.Location:
        gr = self.getGrid()
        rows = gr.rowCount
        cols = gr.colCount
        if rows > 0 and cols > 0: # bounded grid
            emptyLocs = list()
            for r, row in enumerate(gr.rows):
                for c, item in enumerate(row):
                    if item is not None:
                        emptyLocs.append(grid.Location(r,c))
            if(len(emptyLocs) == 0):
                return None
            r = self.generator.random()
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
                loc = grid.Location(r,c)
                if(gr.isValid(loc) and gr.get(loc) is None):
                    return loc

    def add(self, loc:grid.Location, occupant):
        self.getGrid().put(loc, occupant)
        self.repaint()

    def remove(self, loc:grid.Location):
        r = self.getGrid().remove(loc)
        self.repaint()
        return r

    def repaint(self): 
        if self.frame != None:
            self.frame.repaint

    def __str__(self):
        s = ""
        gr = self.getGrid()
        rmin = 0
        rmax = gr.rowCount - 1
        cmin = 0
        cmax = gr.colCount - 1
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

        for i in range(rmin, rmax):
            for j in range(cmin, cmax):
                obj = gr.get(grid.Location(i,j))
                if obj is None:
                    s += " "
                else:
                    s += str(obj)[0]
            s += "\n"
        return s


    

    




                            




        
