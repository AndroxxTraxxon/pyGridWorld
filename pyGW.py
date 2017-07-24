import tkinter
true = True # for simplicity...
none = None

directionMap = {"north": 0, "northeast": 45, "east": 90, "southeast": 135, "south": 180, "southwest": 225, "west": 270, "northwest": 315}

class Actor :
    def __init__(self, img = None, grid = None, loc = None, color = "blue", dir = 0):
        if grid != None or grid.__class__ == "GridWorld":
             self.__grid = grid
        if loc == None or loc.__class__ != "<class 'tuple'>"or len(loc)!=2:
            self.__loc = (0,0)
        else:
            self.__loc = loc


    def getColor (self):
        return self.color
    def getDirection(self):
        return
    def setDirection(self, direction):
        if isinstance(direction, int):
            self.direction = direction%360
        elif isinstance(direction, str):
            direction = direction.lower()
            if directionMap.has_key(direcion):
                self.direction = directionMap[direction]
            else:
                self.direction = 0
        return
    def setLocation(self):
        return
    def move(self):
        """Moves forward: in the rounded direction that the Actor is facing.
              0 (N)
          7(NW) ^ 1(NE)
      6(W)    <-+->     2(E)
          5(SW) V 3(SE)
              4(S)
        The Actor's direction will be approximated to make the movement comply
        to one of the 8 surrounding location possibilities.
        this function does NOT check for out of bounds, and (should?) throw an error for out of bounds.
        """
        movementVector = (0,0)
        moveDirection = int(round((self.direction%360)/45.0))%8
        if moveDirection == 0: # north
            movementVector = (-1,0 )# row, col
        elif moveDirection == 1: # northeast
            movementVector = (-1,1) # row, col
        elif moveDirection == 2: # east
            movementVector = (0,1)
        elif moveDirection == 3: # southeast
            movementVector = (1,1)
        elif moveDirection == 4: # south
            movementVector = (1,0)
        elif moveDirection == 5: #southwest
            movementVector = (1,-1)
        elif moveDirection == 6: # west
            movementVector = (0,-1)
        elif moveDirection == 7: # northwest
            movementVector = (-1,-1)

        self.loc = (self.loc[0] + movementVector[0], self.loc[1] + movementVector[1])
        #remove self from old loc

        #add self to new grid loc.

        return
    def setColor (self, color):
        self.color = color
        self.ui_el

    def act(self):
        self.direction = (self.direction + 180)%360
        return
    def removeSelfFromGrid(self):
        node = grid.getNode(self.loc)
        node.actor = None
        return True
    def addSelfToGrid(self, grid, loc):
        node = grid.getNode(loc)
        if node.actor != None:
            node.actor.removeSelfFromGrid()
        node.actor = self
        grid.actors.append(self)
        self.grid = grid
        self.loc = loc
        node.updateUI()
        return True

class Node:
    def clickDefault(self):
        # color = "#" + str()
        # self.ui_el.config(bg = "red", text = str(self.loc[0]) + ", " + str(self.loc[1]))
        a = Actor()
        a.addSelfToGrid(self.grid, self.loc)
        return
    def __init__(self, grid, ui_el = None, loc = None, actor = None, clickFunction = None):
        self.grid = grid
        if clickFunction != None:
            self.clickDefault = clickFunction
        if ui_el == None:
            raise ValueError ("A Node must be initialized with an associated UI element. Please assign an element to ui_el.")
        else:
            self.ui_el = ui_el
            if self.grid.elementType == "button":
                self.ui_el.config(command = self.clickDefault) #don't bother with frames, the pain isn't worth it.

        if loc != None  and  str(loc.__class__) == "<class 'tuple'>"  and  len(loc) == 2:
            self.loc = loc
        else:
            raise ValueError ("A Node must be initialized with a location. Please assign an location to loc.\n"+
                "loc: " + str(loc.__class__) + ": length " + str(len(loc)))
        self.actor = actor

    def updateUI(self):
        return False

class GridWorld:
    """A structure to allow the simple learning of Python in an object-oriented fashion"""
    def playButtonPress(self):
        self.playing = not self.playing
        if self.playing == False:
            print("\nPaused!")
        else: print("\nPlaying!")
        self.turn()
        return
    def stepButtonPress(self):
        self.playing = False
        self.turn()
        return
    def __init__(self, width = None, height = None, scale = None, elementType = "button", turnDelay = 200, resizeable = False, autoRun = False):
        if width != None:
            self.width = width
        else:
            self.width = 10

        if height != None:
            self.height = height
        else:
            self.height = 10

        if scale != None:
            self.scale = scale
        else:
            self.scale = 40


        self.actors = []
        self.playing = autoRun # the application will not autoRun
        if(turnDelay.__class__ == (0).__class__):
            self.turnDelay = turnDelay
        else:
            self.turnDelay = 200

        self.elementType = elementType.lower()

        """ Creating the application window """

        self.app = tkinter.Tk()
        self.app.wm_title("Python GridWorld")
        self.mainFrame = tkinter.Frame(self.app,cursor = "cross")

        """ Generating the button grid"""
        self.nodes = {} # an organized structure to store each node/button/frame


        for r in range(self.height):
            self.mainFrame.grid_rowconfigure(r, weight = 1)
            for c in range(self.width):
                if self.elementType == "button":
                    btn = tkinter.Button(self.mainFrame)
                elif self.elementType == "frame":
                    btn = tkinter.Frame(self.mainFrame)
                else:
                    self.elementType = "frame"
                    btn = tkinter.Frame(self.mainFrame)
                btn.config(width = self.scale, height = self.scale, bg = "#ccc")
                btn.grid(row = r, column = c, sticky = tkinter.N+tkinter.S+tkinter.E+tkinter.W)
                if(r * self.width + c - r)%2 == 0:
                    btn.config(bg = "#ddd", cursor = "target")
                node = Node(self, btn, (r,c))
                self.nodes[r,c] = node

        for c in range(self.width):
            self.mainFrame.grid_columnconfigure(c, weight = 1)

        """ Generating the toolbar on the bottom """
        self.botFrame = tkinter.Frame(self.mainFrame, height = self.scale)
        self.botFrame.grid(row = self.height, columnspan = self.width, sticky = tkinter.N+tkinter.S+tkinter.E+tkinter.W)
        self.playButton = tkinter.Button(self.botFrame, command = self.playButtonPress, text = "Play/Pause")
        self.playButton.grid(row = 0, column = 0, columnspan = 2, sticky = tkinter.W)
        self.stepButton = tkinter.Button(self.botFrame, command = self.stepButtonPress, text = "Step")
        self.stepButton.grid(row = 0, column = 2, columnspan = 2, sticky = tkinter.W)
        self.turnLabel = tkinter.Label(self.botFrame, text = "Turn: Not Started")
        self.turnLabel.grid(row = 0, column = 4, columnspan = 2, sticky = tkinter.W)
        #DEBUG: print("Dimensions:\nWidth: " + str(self.mainFrame.winfo_width()) + "\nHeight: "+str(self.mainFrame.winfo_height()))
        self.mainFrame.pack(fill = "both", expand = True)
        #self.mainFrame.grid_propagate(False)
        """ Setting the initial size of the window """
        self.app.geometry(str(self.width * self.scale)+"x"+str((self.height + 1) * self.scale))
        self.app.resizable(width = resizeable, height = resizeable)



    def getNode(self, row = 0, col = 0, loc = None):
        if loc != None and loc.__class__ == (0,0).__class__ and len(loc) >= 2:
            row = loc[0]
            col = loc[1]
        return nodes[row, col]

    def isOccupied(self, loc):
        if self.getNode(loc = loc).actor != None:
            return True
        return False

    def run(self):
        self.turnCount = 0
        if self.playing:
            self.app.after(self.turnDelay, self.turn)
        self.app.mainloop()

    def turn(self):
        print("\n Turn " + str(self.turnCount))
        for a in self.actors:
            a.act()
        if self.playing == True:
            self.app.after(self.turnDelay, self.turn)
        self.turnLabel.config(text = "Turn: " + str(self.turnCount))
        self.turnCount += 1


def test():
    world = GridWorld()
    world.run()
    return
