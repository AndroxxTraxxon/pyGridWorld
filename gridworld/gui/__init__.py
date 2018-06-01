from PyQt5 import QtCore, Qt, QtWidgets, QtGui

import json
import sys
import builtins
import world
import grid
from PyQt5.Qt import QScrollArea

def create_action(parent, text, slot=None,
                  shortcut=None, shortcuts=None, shortcut_context=None,
                  icon=None, tooltip=None,
                  checkable=False, checked=False):
    action = QtWidgets.QAction(text, parent)

    if icon is not None:
        action.setIcon(Qt.QIcon(':/%s.png' % icon))
    if shortcut is not None:
        action.setShortcut(shortcut)
    if shortcuts is not None:
        action.setShortcuts(shortcuts)
    if shortcut_context is not None:
        action.setShortcutContext(shortcut_context)
    if tooltip is not None:
        action.setToolTip(tooltip)
        action.setStatusTip(tooltip)
    if checkable:
        action.setCheckable(True)
    if checked:
        action.setChecked(True)
    if slot is not None:
        action.triggered.connect(slot)

    return action
    
def doNothing():
    pass

class DisplayMap():
    pass
    
class WorldWidget(QtWidgets.QMainWindow):
    count = 0
    def __init__(self, wld): # wld: world.World
        print("Making WorldWidget")
        self.world = wld
        super().__init__(parent = None)
        WorldWidget.count += 1
        with open("gui/guiResources.json") as f:
            self.resources = json.load(f)
        self.displayMap = DisplayMap()
        self.content = QtWidgets.QWidget(parent = self)
        self.display = GridFrame(self.displayMap, self.resources, self.content)
        self.guiController = GUIController(self.display, self.displayMap, self.resources, self.content)
        title = self.windowTitle()
        if title == "":
            title = self.resources['frame']['title']
            self.setWindowTitle(title)
        print("Window Title: {0}".format(title))
        self.move(200,100)
        self.setWindowIcon(Qt.QIcon("gui\\GridWorld.gif"))
        self.makeMenus()
        self.layout = QtWidgets.QVBoxLayout()
        self.messageBox = QtWidgets.QPlainTextEdit(self)
        self.messageBox.setPlainText(self.resources["message"]["default"])
        self.messageBox.setReadOnly(True)
        self.messageBox.setFixedHeight(80)
        self.layout.addWidget(self.messageBox)
        self.layout.addWidget(self.display)
        self.layout.addWidget(self.guiController.controlPanel)
        self.content.setLayout(self.layout)
        self.setCentralWidget(self.content)
#         self.graphicsView.

        self.show()
        self.postShowResize()
        self.display.setGrid(self.world.getGrid())
        
        
        
    def makeMenus(self):
        self.menuItemsDisabledDuringRun = list()
        self.makeFileMenu()
        self.makeRunMenu()
        self.makeViewMenu()
        
    def makeFileMenu(self):
        fileMenu = Qt.QMenu(self.resources['dialog']['menu']['file']['title'], self)
        fileMenu.addAction(self.makeAction(self.resources['dialog']['menu']['file']['new'], self.newWorld))
        fileMenu.addAction(self.makeAction(self.resources['dialog']['menu']['file']['save'], self.saveWorld))
        fileMenu.addAction(self.makeAction(self.resources['dialog']['menu']['file']['quit'], Qt.qApp.quit))
        self.menuBar().addMenu(fileMenu)
        
    def makeRunMenu(self):
        runAction = Qt.QAction(self.resources['dialog']['menu']['run']['title'], self)
        runAction.triggered.connect(self.runWorld)
        self.menuBar().addAction(runAction)
        
    def makeViewMenu(self):
        viewMenu = Qt.QMenu(self.resources['dialog']['menu']['view']['title'], self)
        viewMenu.addAction(self.makeAction(self.resources['dialog']['menu']['view']['zoomin'], self.zoomin))
        viewMenu.addAction(self.makeAction(self.resources['dialog']['menu']['view']['zoomout'], self.zoomout))
        viewMenu.addAction(self.makeAction(self.resources['dialog']['menu']['view']['up'], self.panUp))
        viewMenu.addAction(self.makeAction(self.resources['dialog']['menu']['view']['down'], self.panDown))
        viewMenu.addAction(self.makeAction(self.resources['dialog']['menu']['view']['left'], self.panLeft))
        viewMenu.addAction(self.makeAction(self.resources['dialog']['menu']['view']['right'], self.panRight))
        viewMenu.addAction(self.makeAction(self.resources['dialog']['menu']['view']['delete'], self.deleteItem))
        viewMenu.addAction(self.makeAction(self.resources['dialog']['menu']['view']['center'], self.centerView))
        self.menuBar().addMenu(viewMenu)
        
    def postShowResize(self):
        self.guiController.speedSlider.setMinimumWidth(int(self.display.width()/4))
        self.display.setMinimumHeight(self.display.width())
        self.display.setMinimumWidth(self.display.height())
        
    
    def zoomin(self):
        print("zoomIn")
    
    def zoomout(self):
        print("zoomOut")
        
    def panUp(self):
        print("panUp")
        
    def panDown(self):
        print("panDown")
    
    def panLeft(self):
        print("panLeft")
        
    def panRight(self):
        print("panRight")
        
    def deleteItem(self):
        print("deleteItem")
        
    def centerView(self):
        print("centerView")
        
    def newWorld(self):
        print("newWorld")
        
    def saveWorld(self):
        print("saveWorld")
    
    def runWorld(self):
        print("runWorld")        
    
    def makeAction(self, settings:dict, fun = None) -> Qt.QAction:
#         print(settings)
        action = Qt.QAction(settings["title"], self)
        try:
            action.setShortcut(settings["shortcut"])
        except:
            pass
        if fun is not None:
            action.triggered.connect(fun)
            
        return action
            
        
    def keyPressEvent(self, e:Qt.QKeyEvent):
#         print("keyPress:{0}".format(e.key()))
        pass
    
    def closeEvent(self, e:Qt.QCloseEvent):
        WorldWidget.count -= 1

class GridScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.gridLines = []
        self.actors = []
        self.setOpacity(1)
        #self.set_visible(False)
        #self.delete_grid()
        

    def drawGrid(self, gr:grid.Grid, cellSize = None):
        if cellSize is None:
            cellSize = self.DEFAULT_CELL_SIZE
        width = gr.getNumCols() * cellSize
        height = gr.getNumRows() * cellSize
        self.setSceneRect(0, 0, width, height)
        self.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)

        pen = Qt.QPen(Qt.QColor(0,0,0), 2, Qt.Qt.SolidLine)
#         print(self.width())
        for x in range(0,gr.getNumCols()+1):
            xc = x * cellSize
            self.gridLines.append(self.addLine(xc,0,xc,height,pen))

        for y in range(0,gr.getNumRows()+1):
            yc = y * cellSize
            self.gridLines.append(self.addLine(0,yc,width,yc,pen))
            
    def mousePressEvent(self, event):
        self.parent().processLocationClick(self.locationAt(event.scenePos()), event)
        
    def locationAt(self, pt:Qt.QPointF):
        return grid.Location(int(pt.y()/self.parent().cellSize), int(pt.x()/self.parent().cellSize))
    
    def setGridVisible(self,visible=True):
        for line in self.gridLines:
            line.setVisible(visible)

    def deleteGrid(self):
        for line in self.gridLines:
            self.removeItem(line)
        del self.gridLines[:]

    def setOpacity(self,opacity):
        for line in self.gridLines:
            line.setOpacity(opacity)
        
class GridFrame(QtWidgets.QGraphicsView): #GridPanel
    
    MIN_CELL_SIZE = 12
    DEFAULT_CELL_SIZE = 48
    DEFAULT_CELL_COUNT = 10
    TIP_DELAY = 1000
    
    def __init__(self, displayMap:DisplayMap, resources:dict, parent:QtWidgets.QWidget = None, cellSize = None, minCellSize = None):
        super().__init__(parent = parent)
        tmpParent = parent
        while not isinstance(tmpParent, WorldWidget):
            tmpParent = tmpParent.parentWidget()
        self.parentWorld = tmpParent
            
        if minCellSize is None:
            self.minCellSize = self.MIN_CELL_SIZE
        else:
            self.minCellSize = minCellSize
            
        self.setCellSize(cellSize)
        self.resources = resources
        self.displayMap = displayMap
        self.gridScene = GridScene(self)
        self.setScene(self.gridScene)
#         self.setBackgroundBrush(Qt.QBrush(Qt.QColor('lightgray'), Qt.Qt.SolidPattern))
#         self.setForegroundBrush(Qt.QBrush(Qt.QColor('white'), Qt.Qt.SolidPattern))
        self.viewMenu = Qt.QMenu(self)
        self.createActions()
        self.grid = None
        self.currentLocation = None
        minSize = self.DEFAULT_CELL_SIZE * self.DEFAULT_CELL_COUNT * 2
        self.setMinimumSize(minSize, minSize)
#         self.setGraphicsScene(Qt.QGraphicsScene())

    def processLocationClick(self, loc:grid.Location, event:Qt.QMouseEvent):
        if self.grid is not None:
            if self.grid.isValid(loc):
                self.currentLocation = loc
            else:
                self.currentLocation = grid.Location(0,0)
                
        else:
            self.currentLocation = grid.Location(0,0)
            

    def setCellSize(self, cellSize):
        if cellSize is None:
            cellSize = self.DEFAULT_CELL_SIZE
        self.cellSize = min(max(cellSize, self.minCellSize), self.DEFAULT_CELL_SIZE * 4)
    
#     def resizeEvent(self, event:QtGui.QResizeEvent):
#         if (isinstance(self.grid, grid.BoundedGrid) and 
#             event.oldSize().width() != self.size().width() and
#             event.oldSize().height() != self.size().height()):
#             x_ratio = self.size().width()/(self.grid.getNumCols() * self.cellSize) * 0.99
#             y_ratio = self.size().height()/(self.grid.getNumRows() * self.cellSize) * 0.99
#             self.resetTransform()
#             print(event.oldSize(), self.size())
#         return super().resizeEvent(event)
            
        
    def setGrid(self, gr:grid.Grid):
        self.currentLocation = grid.Location(0,0)
        
        self.grid = gr
        self.originRow = self.originCol = 0
        if self.grid.getNumRows() == -1 and self.grid.getNumCols() == -1:
            self.numRows = self.numCols = 2000
        else:
            self.numRows = self.grid.getNumRows()
            self.numCols = self.grid.getNumCols()
        self.repaint()
        self.fitInView(Qt.QRectF(0,0, 
                              self.cellSize * gr.getNumCols(), 
                              self.cellSize * gr.getNumRows()
                       ), Qt.Qt.KeepAspectRatio)
            
            
    def createActions(self):
        act = create_action(self.viewMenu, "Zoom in",
                            slot=self.zoomIn,
                            shortcut="Ctrl+=", 
                            shortcut_context=Qt.Qt.WidgetShortcut)
        self.viewMenu.addAction(act)
 
        act = create_action(self.viewMenu, "Zoom out",
                            slot=self.zoomOut,
                            shortcut=Qt.QKeySequence("Ctrl+-"), 
                            shortcut_context=Qt.Qt.WidgetShortcut)
        self.viewMenu.addAction(act)
        self.addActions(self.viewMenu.actions())
             
    def zoomIn(self):
        if not self.scene():
            return
        self.scale(1.5, 1.5)
 
    def zoomOut(self):
        if not self.scene():
            return
        self.scale(1.0 / 1.5, 1.0 / 1.5)
        
    def panLeft(self):
        self.translate(self.cellSize, self.cellSize)
    
        
    def drawForeground(self, painter, rect):
#         pass
#         print("My grid: " + str(self.grid))
        if self.grid is not None:
            self.gridScene.drawGrid(self.grid, self.cellSize)
         
        return super().drawForeground(painter, rect)
                
    def drawBackground(self, painter, rect):
#         gr = rect.toRect()
#         start_x = gr.left() + self.cellSize - (gr.left() % self.cellSize)
#         start_y = gr.top() + self.cellSize - (gr.top() % self.cellSize)
#         painter.save()
#         painter.setPen(Qt.QColor(0,0,0))
#         painter.setOpacity(0.7)
#  
#         for x in range(start_x, gr.right(), self.cellSize):
#             painter.drawLine(x, gr.top(), x, gr.bottom())
#  
#         for y in range(start_y, gr.bottom(), self.cellSize):
#             painter.drawLine(gr.left(), y, gr.right(), y)
#  
#         painter.restore()
        
        super().drawBackground(painter, rect)
        
  
        
        
    
class GUIController:
    INDEFINITE = 0
    FIXED_STEPS = 1
    PROMPT_STEPS = 2
    
    MAX_DELAY_MSECS = 1000
    MIN_DELAY_MSECS = 10
    INITIAL_DELAY = (MAX_DELAY_MSECS + MIN_DELAY_MSECS)/2
    def __init__(self, disp:GridFrame, displayMap:DisplayMap, res:dict, parent:QtWidgets.QWidget = None):
        self.display = disp
        self.displayMap = displayMap
        self.resources = res
        self.timer = Qt.QTimer()
        self.numStepsToRun = 0
        self.numStepsSoFar = 0
        self.running = 1
        self.occupantClasses = set()
        self.makeControls(parent)
        self.bindControls()
    
    def makeControls(self, parent:QtWidgets.QWidget = None):
        self.controlPanel = QtWidgets.QWidget(parent)
        self.layout = QtWidgets.QHBoxLayout()
        self.stepButton = QtWidgets.QPushButton(self.resources['button']['gui']['step'], self.controlPanel)
        self.runButton = QtWidgets.QPushButton(self.resources['button']['gui']['run'], self.controlPanel)
        self.stopButton = QtWidgets.QPushButton(self.resources['button']['gui']['stop'], self.controlPanel)
        self.slowLabel = QtWidgets.QLabel(self.resources['slider']['slow'], self.controlPanel)
        self.speedSlider = QtWidgets.QSlider(Qt.Qt.Horizontal, parent = self.controlPanel)
        self.speedSlider.setRange(self.MIN_DELAY_MSECS-self.MIN_DELAY_MSECS, self.MAX_DELAY_MSECS)

        self.fastLabel = QtWidgets.QLabel(self.resources['slider']['fast'], self.controlPanel)
        self.layout.addWidget(self.stepButton)
        self.layout.addWidget(self.runButton)
        self.layout.addWidget(self.stopButton)
        self.layout.addWidget(self.slowLabel)
        self.layout.addWidget(self.speedSlider)
        self.layout.addWidget(self.fastLabel)
        self.controlPanel.setLayout(self.layout)

    def bindControls(self):
        self.stepButton.clicked.connect(self.step)
        self.runButton.clicked.connect(self.run)
        self.stopButton.clicked.connect(self.stop)
#         self.speedSlider.changeEvent.connect(self.speedChange)
        self.speedSlider.sliderReleased.connect(self.speedChange)

    def step(self):
        print(self.__class__, "step")
        
    def run(self):
        print(self.__class__, "run")
        
    def stop(self):
        print(self.__class__, "stop")
        
    def speedChange(self):
        print(self.__class__, "speedChange")