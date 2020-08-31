
from gridworld.colors import Color
from gridworld.grid import Grid, UnboundedGrid, BoundedGrid, Location
from gridworld.world import World

import glob
import os
from PIL import Image, ImageTk
import sys
from time import sleep
from threading import Timer
import tkinter as tk
from queue import Queue


root = tk.Tk()
root.overrideredirect(1)
root.withdraw()
root.overrideredirect(0) 

dir_path = os.path.dirname(os.path.realpath(__file__))
resource_path = os.path.join(dir_path, 'resources')
icon_path = os.path.join(resource_path, 'ui', 'GridWorld.gif')
root.wm_iconphoto(True, ImageTk.PhotoImage(Image.open(icon_path)))


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
        super().__init__(root, padx=5, pady=5)

        self.overrideredirect(1)
        self.withdraw()
        self.overrideredirect(0)
        self.visible = False
        self.running = True
        self.ui_update_actions = Queue()

        self.world = world
        self.__class__.count += 1
        self.resources = dict()
        self.grid_classes = (BoundedGrid, UnboundedGrid)
        self.wm_title('GridWorld')
        
        self.make_menus()

        self.message = tk.StringVar()
        self.message_area = tk.Message(self, 
            textvariable=self.message, 
            bg="lemon chiffon", 
            anchor=tk.NW, 
            width=480,
            relief="groove"
        )
        self.message.set("Click on a grid location to construct or manipulate an actor.")
        self.message_area.pack(side="top", fill="x", padx=5)
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
            # sleep(GUIController.MIN_DELAY_MSECS/2000)

    def rerender(self):
        self.display.render()

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
    DEFAULT_BORDER_WIDTH:int = 1
    TIP_DELAY:int = 1000

    grid:Grid
    num_rows:int
    num_cols:int
    origin_row:int
    origin_col:int
    cell_size:int
    line_width:int
    tooltips_enabled:bool
    current_location:Location
    image_sources:dict

    def __init__(self, parent:WorldFrame):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.tooltips_enabled = True
        self.origin_row = 0
        self.origin_col = 0
        self.cell_size = self.DEFAULT_CELL_SIZE
        self.line_width = self.DEFAULT_BORDER_WIDTH
        self.current_location = Location(0,0)
        self.image_sources = dict()
        try:
            self.grid = parent.world.getGrid()
            self.num_cols = self.grid.colCount
            self.num_rows = self.grid.rowCount
        except:
            self.num_cols = self.DEFAULT_CELL_COUNT
            self.num_rows = self.DEFAULT_CELL_COUNT



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
        width = self.num_cols * (self.cell_size + self.line_width)
        height = self.num_rows * (self.cell_size + self.line_width)
        if hasattr(self, 'canvas'):
            self.canvas.destroy()
        self.canvas = tk.Canvas(self, 
            bg=str(Color.GRAY53),
            width=width, height=height,
            bd=None,
            relief="groove",
            scrollregion=(
                -self.line_width, 
                -self.line_width,
                width, height
            ),
        )
        self.canvas.create_rectangle(
            0,0, 
            width,height, 
            fill=str(Color.WHITE),
            width=self.line_width
        )
        self.drawGridLines()
        self.drawOccupants()
        self.drawCurrentLocation()

        self.canvas.pack(
            anchor=tk.NW,
            padx=self.line_width,
            pady=self.line_width,
            ipadx=self.line_width,
            ipady=self.line_width,
            fill=tk.BOTH,
            expand=True,
        )

    def drawGridLines(self):
        width = self.num_cols * (self.cell_size + self.line_width)
        height = self.num_rows * (self.cell_size + self.line_width)
        self.canvas.create_line(0,0, 0,height, fill=str(Color.BLACK), width=self.line_width)
        self.canvas.create_line(0,0, width,0, fill=str(Color.BLACK), width=self.line_width)
        for row_index in range(1,self.num_rows):
            self.canvas.create_line(
                0,      (self.cell_size + self.line_width) * row_index,
                width,  (self.cell_size + self.line_width) * row_index,
                width=self.line_width
            )
        for col_index in range(1,self.num_cols):
            self.canvas.create_line(
                (self.cell_size + self.line_width) * col_index, 0,
                (self.cell_size + self.line_width) * col_index, height,
                width=self.line_width
            )

    def drawOccupants(self):
        self.usedImages = []
        for loc in self.grid.occupiedLocations:
            occupant = self.grid.get(loc)
            if occupant is not None:
                xleft = (self.cell_size + self.line_width) * loc.col + 1
                ytop = (self.cell_size + self.line_width) * loc.row + 1
                self.drawOccupant(xleft, ytop, occupant)

    def drawOccupant(self, xleft:int, ytop:int, occupant):
        try:
            image = self.generate_image(occupant)
            assert image is not None
            self.usedImages.append(image)
            self.canvas.create_image(
                int(xleft + self.cell_size/2), 
                int(ytop + self.cell_size/2), 
                image=image,
                anchor=tk.CENTER,
                )
        except:
            self.canvas.create_text(
                xleft, 
                ytop, 
                text=occupant.__class__.__name__,
                anchor=tk.NW,
            )

    def generate_image(self, occupant):
        base_image = self.get_source_image(occupant.__class__.__name__)
        base_image.thumbnail((self.cell_size, self.cell_size))
        image = base_image.rotate(-occupant.direction)
        return ImageTk.PhotoImage(image)

    def get_source_image(self, name):
        if name in self.image_sources:
            return self.image_sources.get(name).copy()
        path = self.search_for_image(name)
        if path is None:
            return None
        image = Image.open(path)
        maxsize = (480, 480)
        image.thumbnail(maxsize, Image.ANTIALIAS) # no need for the images to be huge. crop this down.
        self.image_sources[name] = image
        return image.copy()
        

    @staticmethod
    def search_for_image(name):
        paths_to_search = [
            os.getcwd(),
            resource_path,
            *sys.path
        ]
        image_endings = [
            "jpg", "jpeg",
            "png", "gif"
        ]
        for path in paths_to_search:
            for ending in image_endings:
                g = glob.glob(os.path.join(path, '**', f'{name}.{ending}'), recursive=True)
                if g:
                    return g[0]
        return None

    def drawCurrentLocation(self):
        row = self.current_location.row
        col = self.current_location.col
        self.canvas.create_rectangle(
            (self.cell_size + self.line_width) * col,
            (self.cell_size + self.line_width) * row,
            (self.cell_size + self.line_width) * (col+1),
            (self.cell_size + self.line_width) * (row+1),
            width=self.line_width+1
        )

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
        super().__init__(parent, padx=5, height=50)
        self.resources = res
        self.display = disp
        self.parent_frame = parent
        
        self.occupant_classes = set()

        self.delay_time = tk.IntVar()
        self.delay_time.set(self.INITIAL_DELAY)
        self.makeControls()
        self.reset_timer()
        world = self.parent_frame.world
        self.pack(fill="x", side="bottom", expand=True)
        self.num_steps_to_run = 0
        self.num_steps_so_far = 0
        self.running = False

    def makeControls(self):
        self.step_button = tk.Button(self, text="Step", command=self.step)
        self.step_button.pack(side="left", padx=5, pady=5, ipadx=5, ipady=2)
        self.run_button = tk.Button(self, text="Start", command=self.run)
        self.run_button.pack(side="left", padx=5, pady=5, ipadx=5, ipady=2)
        self.stop_button = tk.Button(self, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_button.pack(side="left", padx=5, pady=5, ipadx=5, ipady=2)
        slow_label = tk.Label(self, text="Slow")
        fast_label = tk.Label(self, text="Fast")
        fast_label.pack(side="right", padx=5, pady=5)
        
        speed_slider = tk.Scale(
            self, 
            orient=tk.HORIZONTAL, 
            variable=self.delay_time,
            from_=self.MAX_DELAY_MSECS,
            to=self.MIN_DELAY_MSECS,
            resolution=5,
            showvalue=False,
        )
        
        speed_slider.pack(side="right", padx=5, pady=5)
        slow_label.pack(side="right", padx=5, pady=5)

    def run(self):
        self.display.setToolTipsEnabled(False)
        self.parent_frame.setRunMenuItemsEnabled(False)
        self.stop_button.configure(state=tk.NORMAL)
        self.step_button.configure(state=tk.DISABLED)
        self.run_button.configure(state=tk.DISABLED)
        self.num_steps_so_far = 0
        self.running = True
        self.reset_timer()

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
        def action():
            self.parent_frame.world.step()
            self.parent_frame.rerender()
            self.num_steps_so_far += 1
            if self.num_steps_so_far == self.num_steps_to_run:
                self.stop()
            # grid = self.parent_frame.world.getGrid()
            self.reset_timer()
        self.parent_frame.ui_update_actions.put(action)
        
        




    


