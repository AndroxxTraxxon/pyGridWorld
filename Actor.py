class Actor :
    directionMap = {
        "north": 0,
        "northeast": 45,
        "east": 90,
        "southeast": 135,
        "south": 180,
        "southwest": 225,
        "west": 270,
        "northwest": 315
        }

    def __init__(self, img = None, grid = None, loc = None, color = "blue", dir = 0):
        if grid != None or grid.__class__ == "GridWorld":
             self.__grid = grid
        if loc == None or loc.__class__ != "<class 'tuple'>"or len(loc)!=2:
            self.__loc = (0,0)
        else:
            self.__loc = loc
        self.direction = 0

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
