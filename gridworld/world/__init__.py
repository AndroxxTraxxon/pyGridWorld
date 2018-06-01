from grid import BoundedGrid, Grid, Location, UnboundedGrid
from random import randint, gauss
from PyQt5.Qt import qApp, QApplication
import gui
import sys

class World():
    DEFAULT_ROWS = 10
    DEFAULT_COLS = 10
    def __init__(self, g:Grid):
        print("Making World")
        self.message = None
        self.frame = None
        if g is None:
            g = BoundedGrid(self.DEFAULT_ROWS, self.DEFAULT_COLS)
        self.gr = g
        self.gridClassNames = set()
        self.occupantClassNames = set()
        self.addGridClass("BoundedGrid")
        self.addGridClass("UnboundedGrid")
        
        
    def show(self):
        if self.frame is None:
            qApp = QApplication(sys.argv)
            print("Showing World!")
            self.frame = gui.WorldWidget(self)
            qApp.exec_()
        else:
            self.frame.repaint()
    
    def getGrid(self) -> Grid:
        return self.gr
            
    def setGrid(self, newGrid:Grid):
        self.gr = newGrid
        self.repaint()
        
    def setMessage(self, newMessage:str):
        self.message = newMessage
        self.repaint()
        
    def getMessage(self) -> str:
        return self.message
    
    def step(self):
        self.repaint()
        
    def locationClicked(self, loc:Location) -> bool:
        return False
    
    def keyPressed(self, description:str, loc:Location):
        return False
    
    def getRandomEmptyLocation(self) -> Location:
        rows = self.gr.getNumRows()
        cols = self.gr.getNumCols()
        
        if rows > 0 and cols > 0:
            # bounded grid
            emptyLocs = list()
            for row in range(rows):
                for col in range(cols):
                    loc = Location(row, col)
                    if self.gr.isValid(loc) and self.gr.get(loc) is not None:
                        emptyLocs.append(loc)
            if len(emptyLocs) == 0:
                return None
            r = randint(0, len(emptyLocs)-1)
            return emptyLocs[r]
        else:
            # unbounded grid
            while True:
                r, c = None, None
                if rows < 0:
                    r += int(self.DEFAULT_ROWS * gauss(0.5, 0.2))
                else:
                    r = randint(0, rows - 1)
                if cols < 0:
                    c += int(self.DEFAULT_COLS * gauss(0.5, 0.2))
                else:
                    c = randint(0, cols - 1)
                loc = Location(r,c)
                if self.gr.isValid(loc) and self.gr.get(loc) is None:
                    return loc
    
    def add(self, loc:Location, occupant):
        self.getGrid().put(loc, occupant)
        self.repaint()
        
    def remove(self, loc:Location):
        r = self.getGrid().remove(loc)
        self.repaint()
        return r
    
    def addGridClass(self, className:str):
        self.gridClassNames.add(className)
            
    def addOccupantClass(self, className:str):
        self.occupantClassNames.add(className)
        
    def getGridClasses(self) -> set:
        return self.gridClassNames
    
    def getOccupantClasses(self) -> set:
        return self.occupantClassNames
    
    def repaint(self):
        if self.frame is not None:
            self.frame.repaint()
    
    def __str__(self):
        s = ""
        gr = self.getGrid()
        
        rmin = 0
        rmax = gr.getNumRows()-1
        cmin = 0
        cmax = gr.getNumCols()-1
        if rmax < 0 or cmax < 0: # unbounded grid
            for loc in self.gr.getOccupiedLocations():
                r = loc.getRow()
                c = loc.getCol()
                if r < rmin:
                    rmin = r
                elif r > rmax:
                    rmax = r
                if c < cmin:
                    cmin = c
                elif c > cmax:
                    cmax = c
                    
        for row in range(rmin, rmax+1):
            for col in range(cmin, cmax + 1):
                obj = self.gr.get(Location(row, col))
                if obj is None:
                    s += " "
                else:
                    s += str(obj)[1]
            s += "\n"
        return s