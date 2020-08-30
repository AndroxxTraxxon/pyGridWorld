import tkinter as tk
from threading import Timer
from queue import Queue
from gridworld.world import World
from gridworld.grid import Grid, UnboundedGrid, BoundedGrid
from gridworld.colors import Color

root = tk.Tk()
root.overrideredirect(1)
root.withdraw()
root.overrideredirect(0) 


class WorldFrame(tk.Toplevel):

    control:"GUIController"
    display:"GridPanel"
    message_area:tk.Message
    message:tk.StringVar
    menuItemsDisabledDuringRun: list
    world: World
    visible:bool
    display_map:"DisplayMap"
    grid_classes:tuple
    newGridMenu:tk.Menu

    # classwide variables
    count:int = 0
    def __init__(self, world:World):
        super().__init__(root)

        self.overrideredirect(1)
        self.withdraw()
        self.overrideredirect(0)
        self.visible = False
        self.running = True

        self.world = world
        self.__class__.count += 1
        self.resources = dict()
        self.grid_classes = (BoundedGrid, UnboundedGrid)
        self.wm_title('GridWorld')
        
        self.make_menus()

        self.message = tk.StringVar()
        self.message_area = tk.Message(self, textvariable=self.message, bg="lemon chiffon", anchor=tk.NW, width=480)
        self.message.set("Click on a grid location to construct or manipulate an actor.")
        self.message_area.pack(side="top", fill="x")
        self.ui_update_actions = Queue()
        self.display = GridPanel(self)
        self.control = GUIController(self, self.display, self.resources)
        self.wm_resizable(width=True, height=True)

        

    def setVisible(self, visible:bool):
        if self.visible == visible:
            return
        if not isinstance(visible, bool):
            raise TypeError("visible is not bool type")
        self.visible = visible
        if self.visible:
            self.deiconify()
        else:
            self.withdraw()
            

    def show(self):
        self.running = True
        self.setVisible(True)
        self.rerender()
        self.wm_protocol('WM_DELETE_WINDOW', self.hide)
        self.mainloop()


    def hide(self):
        self.running = False
        self.__class__.count -= 1
        if self.__class__.count == 0:
            exit()
        
    def mainloop(self):
        while self.running:
            while not self.ui_update_actions.empty():
                action_func = self.ui_update_actions.get()
                action_func()
            root.update()
            root.update_idletasks()

    def rerender(self):
        pass

    def make_menus(self):
        mbar = tk.Menu(self)

        # File Menu
        file_menu = tk.Menu(mbar, tearoff=0)
        new_file_menu = tk.Menu(file_menu, tearoff=0)
        for grid_type in self.grid_classes:
            new_file_menu.add_command(
                label=grid_type.__module__ + "." + grid_type.__qualname__,
                command=lambda: self.set_grid(grid_type())
            )
        file_menu.add_cascade(label="Set Grid...", menu=new_file_menu)
        file_menu.add_command(label="Quit", command=lambda:0)
        
        mbar.add_cascade(label="World", menu=file_menu)

        # View Menu
        view_menu=tk.Menu(mbar, tearoff=0)

        mbar.add_cascade(label="Location", menu=view_menu)

        # Help Menu
        help_menu=tk.Menu(mbar, tearoff=0)

        mbar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=mbar)

    def set_grid(self, new_grid:Grid):
        old_grid = self.world.getGrid()
        occupants = [old_grid.get(loc) for loc in old_grid.occupiedLocations]
        self.world.setGrid(new_grid)

    def setRunMenuItemsEnabled(self, enabled:bool):
        pass


class GridPanel(tk.Frame):
    
    MIN_CELL_SIZE:int = 12
    DEFAULT_CELL_SIZE:int = 48
    DEFAULT_CELL_COUNT:int = 10
    TIP_DELAY:int = 1000

    grid:Grid
    num_rows:int
    num_cols:int
    origin_row:int
    origin_col:int
    cell_size:int
    tooltips_enabled:bool

    def __init__(self, parent):
        width=height=self.DEFAULT_CELL_COUNT * self.DEFAULT_CELL_SIZE
        super().__init__(parent, bg=str(Color.LIGHTGREY))
        self.pack(fill=tk.BOTH)
        self.tooltips_enabled = True

    def setToolTipsEnabled(self, enabled):
        if not isinstance(enabled, bool):
            raise TypeError("enabled is not bool")
        if self.tooltips_enabled == enabled:
            return
        self.tooltips_enabled = enabled
        if self.tooltips_enabled:
            #probably do something about it?
            pass
        else:
            pass

    def render(self):
        width=height=self.DEFAULT_CELL_COUNT * self.DEFAULT_CELL_SIZE
        if hasattr(self, 'canvas'):
            self.canvas.destroy()
        self.canvas = tk.Canvas(self, 
            bg="white",
            width=width, height=height
        )

        self.canvas.pack(fill=tk.BOTH)

    def drawGridLines(self):
        pass
    
    def drawOccupants(self):
        pass

    def drawOccupant(self, xleft:int, ytop:int, occupant):
        pass

    def recalculateCellSize(self, min_size=MIN_CELL_SIZE):
        pass

class GUIController(tk.Frame):
    INDEFINITE, FIXED_STEPS, PROMPT_STEPS = 0, 1, 2
    MIN_DELAY_MSECS, MAX_DELAY_MSECS = 10, 1000
    INITIAL_DELAY = MIN_DELAY_MSECS + (MAX_DELAY_MSECS - MIN_DELAY_MSECS) / 2

    timer:Timer
    step_button: tk.Button
    run_button: tk.Button
    stop_button: tk.Button

    control_panel: tk.Frame
    display: GridPanel
    parent_frame: WorldFrame
    num_steps_to_run: int
    num_steps_so_far: int
    resources: dict
    running: bool
    occupant_classes: list

    def __init__(self, parent:WorldFrame, disp:GridPanel, res:dict):
        super().__init__(parent)
        self.resources = res
        self.display = disp
        self.parent_frame = parent
        
        self.occupant_classes = set()

        self.delay_time = tk.IntVar()
        self.delay_time.set(self.INITIAL_DELAY)
        self.makeControls()
        self.reset_timer()
        world = self.parent_frame.world
        self.pack(fill="x", side="bottom")
        self.num_steps_to_run = 0
        self.num_steps_so_far = 0
        self.running = False

    def makeControls(self):
        self.step_button = tk.Button(self, text="Step", command=self.step)
        self.step_button.pack(side="left")
        self.run_button = tk.Button(self, text="Start", command=self.run)
        self.run_button.pack(side="left")
        self.stop_button = tk.Button(self, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_button.pack(side="left")
        slow_label = tk.Label(self, text="Slow")
        fast_label = tk.Label(self, text="Fast")
        fast_label.pack(side="right")
        
        speed_slider = tk.Scale(
            self, 
            orient=tk.HORIZONTAL, 
            variable=self.delay_time,
            from_=self.MAX_DELAY_MSECS,
            to=self.MIN_DELAY_MSECS,
            resolution=5,
            showvalue=False,
        )
        
        speed_slider.pack(side="right")
        slow_label.pack(side="right")

    def run(self):
        self.display.setToolTipsEnabled(False)
        self.parent_frame.setRunMenuItemsEnabled(False)
        self.stop_button.configure(state=tk.NORMAL)
        self.step_button.configure(state=tk.DISABLED)
        self.run_button.configure(state=tk.DISABLED)
        self.num_steps_so_far = 0
        self.running = True
        self.timer.start()

    def stop(self):
        self.running = False
        self.display.setToolTipsEnabled(True)
        self.parent_frame.setRunMenuItemsEnabled(True)
        self.stop_button.configure(state=tk.DISABLED)
        self.step_button.configure(state=tk.NORMAL)
        self.run_button.configure(state=tk.NORMAL)
        self.reset_timer()

    def reset_timer(self):
        def action():
            if hasattr(self, 'timer') and self.timer.is_alive():
                self.timer.cancel()
            self.timer = Timer(self.delay_time.get()/1000, self.step)
            if self.running:
                self.timer.start()
        self.parent_frame.ui_update_actions.put(action)

    def step(self):
        self.parent_frame.world.step()
        self.parent_frame.rerender()
        self.num_steps_so_far += 1
        print("step " + str(self.num_steps_so_far))
        if self.num_steps_so_far == self.num_steps_to_run:
            self.stop()
        # grid = self.parent_frame.world.getGrid()
        self.reset_timer()




    


