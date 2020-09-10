
from gridworld.colors import Color, primaries as primary_colors
from gridworld.grid import Grid, UnboundedGrid, BoundedGrid, Location
from gridworld.world import World
from gridworld.timer import RepeatTimer
import inspect

import glob
import os
from PIL import Image, ImageTk, ImageOps
import sys
from time import time, sleep
from threading import Thread, Event
import tkinter as tk
import tkinter.dialog as dialog
import tkinter.messagebox as messagebox
from queue import Queue

root = tk.Tk()
root.overrideredirect(1)
root.withdraw()
root.overrideredirect(0) 

dir_path = os.path.dirname(os.path.realpath(__file__))
resource_path = os.path.join(dir_path, 'resources')
icon_path = os.path.join(resource_path, 'ui', 'GridWorld.gif')
root.wm_iconphoto(True, ImageTk.PhotoImage(Image.open(icon_path)))


def _search_for_image(name):
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


class WorldFrame(tk.Toplevel):

    display:"GridPanel"
    message_area:tk.Message
    message:tk.StringVar
    menuItemsDisabledDuringRun: list
    world: World
    visible:bool
    display_map:"DisplayMap"
    grid_classes:tuple
    newGridMenu:tk.Menu

    # private variables
    __needs_render:bool
    _control:"GUIController" = None

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
        

        self.message = tk.StringVar()
        self.message_area = tk.Message(self, 
            textvariable=self.message, 
            bg="lemon chiffon", 
            anchor=tk.NW, 
            width=480,
            relief="groove"
        )
        self.message.set("Click on a grid location to construct or manipulate an actor.")
        self.message_area.pack(side=tk.TOP, fill=tk.X, padx=5)
        self.display = GridPanel(self)
        self.control = GUIController(self, self.display, self.resources)
        self.control.pack(fill=tk.X, side=tk.BOTTOM, expand=False)
        self.display.pack(fill=tk.BOTH, side=tk.TOP, expand=tk.TRUE)
        self.make_menus()
        self.make_keybindings()
        self.wm_resizable(width=True, height=True)

    @property
    def control(self) -> "GUIController":
        return self._control

    @control.setter
    def control(self, control:"GUIController"):
        self._control = control
        
    def setVisible(self, visible:bool):
        if self.visible == visible:
            return
        if not isinstance(visible, bool):
            raise TypeError("visible is not bool type")
        self.visible = visible
        if self.visible:
            self.deiconify()
            self.update()
            self.update_idletasks()
            self.display.recalculate_cell_size()
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
            if self.control.running:
                self.control.stop()
            exit()
        
    def mainloop(self):
        while self.running:
            while not self.ui_update_actions.empty():
                action_func = self.ui_update_actions.get()
                action_func()
            if self.__needs_render:
                self.__needs_render = False
                self.display.render()
            self.update()
            self.update_idletasks()

    def rerender(self):
        self.__needs_render = True
        

    def make_menus(self):
        mbar = tk.Menu(self)

        # File Menu
        file_menu = tk.Menu(mbar, tearoff=0)
        new_file_menu = tk.Menu(file_menu, tearoff=0)
        for grid_type in self.grid_classes:
            new_file_menu.add_command(
                label=grid_type.__module__ + "." + grid_type.__qualname__,
                command=self.configure_grid_type(grid_type) 
            )
        file_menu.add_cascade(label="Set Grid...", menu=new_file_menu)
        file_menu.add_command(label="Quit", command=self.hide)
        
        mbar.add_cascade(label="World", menu=file_menu)

        # View Menu
        view_menu=tk.Menu(mbar, tearoff=0)
        view_menu.add_command(label="Up", command=lambda:self.display.move_location(-1, 0))
        view_menu.add_command(label="Down", command=lambda:self.display.move_location(1, 0))
        view_menu.add_command(label="Left", command=lambda:self.display.move_location(0, -1))
        view_menu.add_command(label="Right", command=lambda:self.display.move_location(0, 1))
        view_menu.add_command(label="Edit", command=self.control.edit_location)
        view_menu.add_command(label="Delete", command=self.control.delete_location)
        view_menu.add_command(label="Zoom In", command=self.display.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.display.zoom_out)

        mbar.add_cascade(label="Location", menu=view_menu)

        # Help Menu
        help_menu=tk.Menu(mbar, tearoff=0)
        help_menu.add_command(label="About Gridworld...", command=self.show_about)
        help_menu.add_command(label="Gridworld Help...", command=self.show_help)
        help_menu.add_command(label="Show License...", command=self.show_license)

        mbar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=mbar)

    def make_keybindings(self):
        self.bind('<Up>', lambda event:self.display.move_location(-1, 0))
        self.bind('<Down>', lambda event:self.display.move_location(1, 0))
        self.bind('<Left>', lambda event:self.display.move_location(0, -1))
        self.bind('<Right>', lambda event:self.display.move_location(0, 1))
        self.bind('<Return>', lambda event:self.control.edit_location())
        self.bind('<Delete>', lambda event:self.control.delete_location())

    def configure_grid_type(self, grid_type:type):
        def action():
            instance = InstanceBuilder(self, grid_type).evaluate()
            if isinstance(instance, grid_type):
                self.set_grid(instance)
        return action

    def set_grid(self, new_grid:Grid):
        old_grid = self.world.grid
        occupants = dict()
        for loc in tuple(old_grid.occupied_locations):
            occupants[loc] = self.world.remove(loc)
            
        self.world.grid = new_grid
        self.display.grid = new_grid
        for loc, occupant in occupants.items():
            if new_grid.is_valid(loc):
                self.world.add(occupant, loc)
        self.rerender()


    def show_about(self):
        pass

    def show_help(self):
        pass

    def show_license(self):
        pass

    def setRunMenuItemsEnabled(self, enabled:bool):
        pass


class GridPanel(tk.Frame):
    
    # Canvas render tags
    TAG_OCCUPANTS='OCCUPANTS'
    TAG_GRID='GRID'
    TAG_BACKGROUND='BACKGROUND'
    TAG_CURRENTLOC='CURRENTLOC'

    # static constants
    MIN_CELL_SIZE:int = 12
    DEFAULT_CELL_SIZE:int = 48
    DEFAULT_CELL_COUNT:int = 10
    DEFAULT_BORDER_WIDTH:int = 1
    TIP_DELAY:int = 1000

    _grid:Grid
    num_rows:int
    num_cols:int
    origin_row:int
    origin_col:int
    cell_size:int
    bd:int
    _tooltips_enabled:bool
    current_location:Location
    image_sources:dict
    used_images:dict



    def __init__(self, parent:WorldFrame):
        super().__init__(parent)
        self._tooltips_enabled = True
        self.origin_row = 0
        self.origin_col = 0
        self.cell_size = self.DEFAULT_CELL_SIZE
        self.bd = self.DEFAULT_BORDER_WIDTH
        self.current_location = Location(0,0)
        self.image_sources = dict()
        self.used_images = dict()
        self.grid = parent.world.grid
        width = (self.grid.col_count * (self.cell_size + 1)) + (self.bd)
        height = (self.grid.row_count * (self.cell_size + 1)) + (self.bd)
        self.canvas = tk.Canvas(self, 
            bg=str(Color.GRAY53),
            width=width,
            height=height,
            bd=None,
            relief="groove",
            scrollregion=(
                -self.bd, 
                -self.bd,
                width, height
            ),
        )
        self.canvas.pack(
            anchor=tk.NW,
            padx=self.bd,
            pady=self.bd,
            ipadx=self.bd,
            ipady=self.bd,
            fill=tk.BOTH,
            expand=True,
        )
        self.canvas.update()
        self.update()
        self.world = parent.world
        self.render(True)

    @property
    def grid(self) -> Grid:
        return self._grid

    @grid.setter
    def grid(self, grid:Grid):
        try:
            self._grid = grid
            self.current_location = Location(0,0)
            self.origin_col = 0
            self.origin_row = 0
            if self.grid.row_count == -1 and self.grid.col_count == -1:
                self.num_rows = 2000
                self.num_cols = 2000
            else:
                self.num_cols = self.grid.col_count
                self.num_rows = self.grid.row_count
        except:
            self.num_cols = self.DEFAULT_CELL_COUNT
            self.num_rows = self.DEFAULT_CELL_COUNT

        self.recalculate_cell_size(self.MIN_CELL_SIZE)

    @property
    def tooltips_enabled(self) -> bool:
        return self._tooltips_enabled

    @tooltips_enabled.setter
    def tooltips_enabled(self, enabled):
        if not isinstance(enabled, bool):
            raise TypeError("enabled is not bool")
        if self._tooltips_enabled == enabled:
            return
        self._tooltips_enabled = enabled
        if self._tooltips_enabled:
            #probably do something about it?
            pass
        else:
            pass

    def render(self, draw_grid=True, draw_current_loc=True):
        if draw_grid:
            self.draw_grid(True)
        if draw_current_loc:
            self.draw_current_location()
        self.draw_occupants()

    def draw_grid(self, draw_background=False):
        width = self.num_cols * (self.cell_size + 1)
        height = self.num_rows * (self.cell_size + 1)
        self.canvas.delete(self.TAG_GRID)
        if draw_background:
            self.canvas.delete(self.TAG_BACKGROUND)
            self.canvas.create_rectangle(
                0,
                0, 
                width,
                height, 
                fill=str(Color.WHITE),
                width=1,
                tags=self.TAG_BACKGROUND
            )
        self.draw_grid_lines()

    def draw_grid_lines(self):
        width = self.num_cols * (self.cell_size + self.bd)
        height = self.num_rows * (self.cell_size + self.bd)
        for row_index in range(1,self.num_rows):
            self.canvas.create_line(
                0,      self.bd + (self.cell_size + 1) * row_index,
                width,  self.bd + (self.cell_size + 1) * row_index,
                width=self.bd,
                tags=self.TAG_GRID
            )
        for col_index in range(1,self.num_cols):
            self.canvas.create_line(
                self.bd + (self.cell_size + 1) * col_index, 0,
                self.bd + (self.cell_size + 1) * col_index, height,
                width=self.bd,
                tags=self.TAG_GRID
            )

    def draw_occupants(self):
        self.canvas.delete(self.TAG_OCCUPANTS)

        for loc in self.grid.occupied_locations:
            occupant = self.grid.get(loc)
            if occupant is not None:
                x,y = self.point_for_location(loc)
                self.draw_occupant(x, y, occupant)

    def draw_occupant(self, x:int, y:int, occupant):
        image = None
        occ_desc = "{name}[col:{color}; dir:{direction}]".format(
            name=occupant.__class__.__name__,
            color=str(occupant.color),
            direction=str(int(occupant.direction))
        )
        if occ_desc in self.used_images:
            image = self.used_images.get(occ_desc)

        else:
            image = self.generate_image(occupant)
            self.used_images[occ_desc] = image
        if image is not None:
            self.canvas.create_image(
                int(x), 
                int(y), 
                image=image,
                anchor=tk.CENTER,
                tags=self.TAG_OCCUPANTS
                )
        else:
            self.canvas.create_text(
                x - self.cell_size//2, 
                y - self.cell_size//2, 
                text=occupant.__class__.__name__[0:4],
                anchor=tk.NW,
                tags=self.TAG_OCCUPANTS
            )

    def generate_image(self, occupant):
        image = self.get_source_image(occupant)
        if image:
            image.thumbnail((self.cell_size, self.cell_size))
            if hasattr(occupant, 'color') and isinstance(occupant.color, Color):
                greyscale = ImageOps.grayscale(image)
                h,s,v = occupant.color.hsv
                white_map = Color.from_hsv(h,s,min(1.0, v*2))
                colorized = ImageOps.colorize(
                    greyscale, 
                    Color.GRAY15.rgb, 
                    white_map.rgb, 
                    mid=occupant.color.rgb,
                    midpoint=80
                )
                try:
                    a = image.getchannel('A')
                    colorized.putalpha(a)
                except:
                    pass
                image = colorized.rotate(-occupant.direction)
            output = ImageTk.PhotoImage(image)
            return output
        return None

    def get_source_image(self, obj):
        if isinstance(obj, type):
            _cls = obj
        else:
            _cls = obj.__class__
        while _cls is not None:
            name = _cls.__name__
            if name in self.image_sources:
                return self.image_sources.get(name).copy()
            path = _search_for_image(name)
            if path is None:
                _cls = _cls.__base__
                continue
            image = Image.open(path)
            maxsize = (480, 480)
            image.thumbnail(maxsize, Image.ANTIALIAS) # no need for the images to be huge. crop this down.
            self.image_sources[name] = image
            return image.copy()
        return None

    def draw_current_location(self):
        self.canvas.delete(self.TAG_CURRENTLOC)
        x,y = self.point_for_location(self.current_location)
        d = self.cell_size//2
        self.canvas.create_rectangle(
            x - d,
            y - d,
            x + d,
            y + d,
            width=self.bd+1,
            tags=self.TAG_CURRENTLOC
        )

    def recalculate_cell_size(self, min_size=MIN_CELL_SIZE):
        if self.winfo_width() > 1: # the window and widget have to actually be visible on the screen
            if self.num_rows == 0 or self.num_cols == 0:
                self.cell_size = 0
            else:
                root.update_idletasks()
                root.update()
                desired_size = min(
                    (self.winfo_height() - (self.DEFAULT_BORDER_WIDTH * 2))/self.num_rows,
                    (self.winfo_width() - (self.DEFAULT_BORDER_WIDTH * 2))/self.num_cols
                ) - 1
                self.cell_size = self.DEFAULT_CELL_SIZE
                if self.cell_size <= desired_size:
                    while 2 * self.cell_size <= desired_size:
                        self.cell_size *= 2
                else:
                    while (self.cell_size // 2) >= max(desired_size, min_size):
                        self.cell_size //= 2
        # self.cell_size = self.DEFAULT_CELL_SIZE

    def move_location(self, dr, dc):
        new_location = Location(
            self.current_location.row + dr,
            self.current_location.col + dc,
        )
        if not self.grid.is_valid(new_location):
            return
        self.current_location = new_location
        if self.is_pannable_unbounded():
            if self.origin_row > self.current_location.row:
                self.origin_row = self.current_location.row
            if self.origin_col > self.current_location.col:
                self.origin_col = self.current_location.col

            rows = int(self.winfo_height()) // (self.cell_size + 1)
            cols = int(self.winfo_width()) // (self.cell_size + 1)
            if self.origin_row + rows - 1 < self.current_location.rows:
                self.origin_row = self.current_location.row - rows + 1
            if self.origin_col + cols - 1 < self.current_location.col:
                self.origin_col = self.current_location - cols + 1
        else:
            dx = 0
            dy = 0
            point_x, point_y = self.point_for_location(self.current_location)
            left = point_x - (self.cell_size // 2)
            right = point_x + (self.cell_size // 2)
            top = point_y - (self.cell_size // 2)
            bottom = point_y + (self.cell_size // 2)
            

        self.draw_current_location()

    def point_for_location(self, loc:Location):
        return (
            self.col_to_x_coord(loc.col) + self.cell_size // 2,
            self.row_to_y_coord(loc.row) + self.cell_size // 2
        )

    def col_to_x_coord(self, col:int) -> int:
        return (col - self.origin_col) * (self.cell_size + 1) + 1 + self.DEFAULT_BORDER_WIDTH

    def row_to_y_coord(self, row:int) -> int:
        return (row - self.origin_row) * (self.cell_size + 1) + 1 + self.DEFAULT_BORDER_WIDTH
    
    def is_pannable_unbounded(self) -> bool:
        return self.grid is not None and (
            self.grid.row_count == -1 or 
            self.grid.col_count == -1
        )

    def zoom_in(self):
        pass

    def zoom_out(self):
        pass


class GUIController(tk.Frame):
    INDEFINITE, FIXED_STEPS, PROMPT_STEPS = 0, 1, 2
    MIN_DELAY_MSECS, MAX_DELAY_MSECS = 20, 1000
    INITIAL_DELAY = MIN_DELAY_MSECS + (MAX_DELAY_MSECS - MIN_DELAY_MSECS) / 2

    timer:RepeatTimer
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
        super().__init__(parent, padx=5, height=500, relief=tk.GROOVE, bd=2)
        self.resources = res
        self.display = disp
        self.parent_frame = parent
        self.occupant_classes = parent.world.occupant_types
        self.delay_time = tk.IntVar()
        self.delay_time.set(self.INITIAL_DELAY)
        self.__make_controls()
        self.num_steps_to_run = 0
        self.num_steps_so_far = 0
        self.timer = None
        self.running = False

    def __make_controls(self):
        self.step_button = tk.Button(self, text="Step", command=self.step)
        self.step_button.pack(side="left", pady=2, ipadx=10, ipady=1)
        self.run_button = tk.Button(self, text="Run", command=self.run)
        self.run_button.pack(side="left", padx=10, pady=2, ipadx=10, ipady=1)
        self.stop_button = tk.Button(self, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_button.pack(side="left", pady=2, ipadx=10, ipady=1)
        slow_label = tk.Label(self, text="Slow")
        fast_label = tk.Label(self, text="Fast")
        fast_label.pack(side="right", padx=5, pady=2)
        
        speed_slider = tk.Scale(
            self, 
            orient=tk.HORIZONTAL, 
            variable=self.delay_time,
            from_=self.MAX_DELAY_MSECS,
            to=self.MIN_DELAY_MSECS,
            resolution=5,
            showvalue=False,
            command=self.__update_delay_time
        )
        
        speed_slider.pack(side="right", padx=5, pady=5)
        slow_label.pack(side="right", padx=5, pady=5)

        self.display.canvas.bind('<Button-1>', self.handle_click)
        self.display.canvas.bind('<Button-3>', self.handle_click)

    def __update_delay_time(self, delay):
        if self.timer is not None:
            self.timer.delay_ms = int(delay)

    def run(self):
        self.display.tooltips_enabled = False
        self.parent_frame.setRunMenuItemsEnabled(False)
        self.stop_button.configure(state=tk.NORMAL)
        self.step_button.configure(state=tk.DISABLED)
        self.run_button.configure(state=tk.DISABLED)
        self.num_steps_so_far = 0
        self.running = True
        if(hasattr(self, 'timer') and self.timer is not None):
            self.timer.stop()
            self.timer.join()
        self.timer = RepeatTimer(self.step, self.delay_time.get())
        self.timer.start()

    def stop(self):
        self.running = False
        self.display.tooltips_enabled = True
        self.parent_frame.setRunMenuItemsEnabled(True)
        self.stop_button.configure(state=tk.DISABLED)
        self.step_button.configure(state=tk.NORMAL)
        self.run_button.configure(state=tk.NORMAL)
        self.timer.stop()
        self.timer.join(0.01)

    def step(self):
        self.parent_frame.world.step()
        self.num_steps_so_far += 1
        if self.num_steps_so_far == self.num_steps_to_run:
            self.stop()

    def __action__create_object_default(self, object_type):
        def action():
            occupant = object_type()
            self.parent_frame.world.add(occupant, self.display.current_location)
            self.display.draw_occupants()
        return action

    def __action__create_object_with_ui(self, object_type):
        def action():
            occupant = InstanceBuilder(self.parent_frame, object_type).evaluate()
            if occupant: # this can come back none if cancelled
                self.parent_frame.world.add(occupant, self.display.current_location)
                self.display.draw_occupants()
        return action

    def __action__call_function(self, function):
        def action():
            value = FunctionCaller(self.parent_frame, function).evaluate()
            self.display.render()
            if value is not None:
                messagebox.showinfo(function.__name__, str(value))
        return action

    def __action__show_value(self, title, value):
        def action():
            messagebox.showinfo(title, str(value))
        return action


    def edit_location(self):
        self.menu_images = list()
        self.menu=tk.Menu(self, tearoff=False)
        occupant = self.display.grid.get(self.display.current_location)
        if occupant is None:
            for name, occ_type in self.parent_frame.world.occupant_types.items():
                img_src = self.display.get_source_image(occ_type)
                image_config = dict()
                if img_src is not None:
                    img_src.thumbnail((12,12), Image.ANTIALIAS)
                    tk_img = ImageTk.PhotoImage(img_src)
                    image_config["image"] = tk_img
                    image_config["compound"] = tk.LEFT
                    self.menu_images.append(tk_img)
                
                if self.menu.index(tk.END) is not None:
                    self.menu.add_separator()
                if InstanceBuilder.can_init_pure_default(occ_type):
                    cmd_label = ".".join((occ_type.__module__, occ_type.__name__))
                    self.menu.add_command(
                        label="%s()"%cmd_label,
                        command=self.__action__create_object_default(occ_type),
                        **image_config
                    )
                cmd_label = ".".join((occ_type.__module__, occ_type.__name__) )
                self.menu.add_command(
                    label="%s(...)" % cmd_label,
                    command=self.__action__create_object_with_ui(occ_type),
                    **image_config
                )    
        else:
            members = dict(((key, value) for key, value in inspect.getmembers(occupant) if not key.startswith("_")))
            callables = dict()
            properties = dict()
            for name, member in members.items():
                if callable(member):
                    callables[name] = member
                else:
                    properties[name] = member
            for name, function in callables.items():
                if FunctionCaller.executable(function):
                    self.menu.add_command(
                        label="%s(...)" % name,
                        command=self.__action__call_function(function)
                    )
            if self.menu.index(tk.END) is not None:
                self.menu.add_separator()
            for name, value in properties.items():
                self.menu.add_command(
                    label="%s" % name,
                    command=self.__action__show_value(name, value)
                )
            
        w_x = self.display.winfo_rootx()
        w_y = self.display.winfo_rooty()
        offset = self.display.DEFAULT_BORDER_WIDTH + self.display.cell_size//2
        menu_x = w_x + offset + (self.display.cell_size + self.display.DEFAULT_BORDER_WIDTH) * self.display.current_location.col
        menu_y = w_y + offset + (self.display.cell_size + self.display.DEFAULT_BORDER_WIDTH) * self.display.current_location.row
        self.menu.post(menu_x, menu_y)
        self.parent_frame.update()

    def delete_location(self):
        world = self.parent_frame.world
        loc = self.display.current_location
        if loc is not None:
            world.remove(loc)
            self.parent_frame.rerender()

    def handle_click(self, event):
        if not self.running:
            # This location positioning might need to be corrected, 
            # but it seems to be working right now.
            loc_row = (event.y - self.display.bd * 3 - 1) // (self.display.cell_size + self.display.bd) + self.display.origin_row
            loc_col = (event.x - self.display.bd * 3 - 1) // (self.display.cell_size + self.display.bd) + self.display.origin_col
            calc_loc = Location(loc_row, loc_col)
            if self.display.grid.is_valid(calc_loc):
                self.display.current_location = calc_loc
                self.display.draw_current_location()
                self.edit_location()


class ParamField:

    _widget:tk.Widget

    @property
    def widget(self) -> tk.Widget:
        return self._widget

    @property
    def value(self):
        raise NotImplementedError()


class StringField(ParamField):

    def __init__(self, parent_widget:tk.Widget, default_value:str = '', widget_options:dict=dict()):
        self._widget = tk.Entry(parent_widget, *widget_options)

    @property
    def value(self):
        return str(self._widget.get())


class NumberField(ParamField):
    __possible_types = (float, int)
    _var:tk.StringVar
    def __init__(self, 
            parent_widget:tk.Widget, 
            default_value:float=1.0,
            step:float=1.0, 
            field_type:type=float, 
            widget_options:dict=dict()
        ):
        self._field_type = field_type
        if default_value is None:
            default_value = 1
        if step is None:
            step = 1
        if field_type not in self.__possible_types:
            raise ValueError('field_type must be one of ' + str(self.__possible_types))
        if field_type is int and step < 1.0:
            step = 1
        self.step = step
        self._var = tk.StringVar(parent_widget)
        self._widget = tk.Spinbox(
            parent_widget, 
            textvariable=self._var, 
            increment=step,
            from_=-1000000,
            to=1000000,
            )
        if default_value is not None:
            self._var.set(str(default_value))

    @property
    def value(self) -> float:
        try:
            val = self._field_type(
                self._var.get()
            )
        except:
            val = None
        return val


class ColorField(ParamField):
    _var:tk.StringVar
    _rand_key = 'RANDOM'
    def __init__(self, parent_widget:tk.Widget, default_value=Color.BLUE, select_options:dict=primary_colors, widget_options:dict=dict()):
        self._var = tk.StringVar(parent_widget)
        if isinstance(default_value, Color):
            self._var.set(default_value.name)
        else:
            self._var.set(str(default_value))
        self.options = [option for option in select_options.keys()]
        self.option_map = select_options
        self.options.append(self._rand_key)
        self._widget = tk.OptionMenu(parent_widget, self._var, *self.options)

    @property
    def value(self) -> Color:
        str_value = self._var.get()
        if str_value == self._rand_key:
            return Color.random()
        else:
            return self.option_map[str_value]


class LocationField(ParamField):
    _row:tk.StringVar
    _col:tk.StringVar
    def __init__(self,
            parent_widget:tk.Widget,
            default_value:Location=Location(0,0),
            widget_options:dict=dict()
        ):

        self._widget = tk.Frame(parent_widget)
        self._row = tk.StringVar(parent_widget)
        self._col = tk.StringVar(parent_widget)
        row_box = tk.Spinbox(
            self._widget,
            textvariable=self._row,
            increment=1,
            from_=-1000000,
            to=1000000,
        )
        row_box.pack(side=tk.LEFT)
        col_box = tk.Spinbox(
            self._widget,
            textvariable=self._col,
            increment=1,
            from_=-1000000,
            to=1000000,
        )
        col_box.pack(side=tk.LEFT)
        if isinstance(default_value, Location):
            self._row.set(str(default_value.row))
            self._col.set(str(default_value.col))
        else:
            self._row.set(str(0))
            self._col.set(str(0))

    @property
    def value(self) -> float:
        try:
            row = int(self._row.get())
            col = int(self._col.get())
            val = Location(row, col)
        except:
            val = None
        return val


class FunctionCaller(tk.Toplevel):

    _parent_window:tk.Toplevel
    _method: type
    _fields:dict
    _finished: bool

    buildable_types = [
        str,
        float,
        int,
        Color,
        Location
    ]

    def __init__(self, parent:tk.Toplevel, method:type):
        self.cancelled = False
        super().__init__(parent, padx=5, pady=5)
        self.wm_withdraw()
        self._parent_window = parent
        self._method = method
        self.wm_protocol('WM_DELETE_WINDOW', self.cancel)
        self._finished = False
        self.field_frame=tk.LabelFrame(self,text=method.__name__)
        self.field_frame.pack(side=tk.TOP, fill=tk.X)
        self._build_fields()
        self.wm_title(method.__name__)
        button_frame = tk.Frame(self)
        confirm_button = tk.Button(button_frame, text='Confirm', command=self.hide)
        confirm_button.pack(side=tk.LEFT)
        cancel_button = tk.Button(button_frame, text='Cancel', command=self.cancel)
        cancel_button.pack(side=tk.RIGHT)
        button_frame.pack(side=tk.TOP, fill=tk.X)
        self.bind("<Return>", lambda event: self.hide())
        self.bind("<Escape>", lambda event: self.cancel())
        self.focus_set()

    def _build_fields(self):
        self._fields = dict()
        parameters = dict(
            inspect.signature(
                self._method
            ).parameters
        )
        if 'self' in parameters:
            del parameters['self'] # don't need to configure this...
        for name, param in parameters.items():
            frame = tk.Frame(self.field_frame)
            field_type = param.annotation
            field_default = None
            if field_type is inspect.Parameter.empty:
                if param.default is inspect.Parameter.empty:
                    raise NotImplementedError(
                'Inspected Classes must mark their __init__ methods with type annotations or ' 
                'default values'
                )
                field_type = type(param.default)
            if param.default is not inspect.Parameter.empty:
                field_default = param.default
            field = self._build_field(frame, field_type, field_default)
            self._fields[name] = field
            label = tk.Label(frame, text=name)
            label.pack(side=tk.LEFT)
            field.widget.pack(side=tk.RIGHT)
            frame.pack(side=tk.TOP, fill=tk.X, expand=True)

    def _build_field(self, frame:tk.Frame, field_type:type, default:object, **kwargs):
        build_map = {
            str.__name__: lambda _default, **kwargs, :StringField(frame, _default, widget_options=kwargs),
            float.__name__:lambda _default, **kwargs, :NumberField(frame, _default, field_type=field_type, widget_options=kwargs),
            int.__name__:lambda _default, **kwargs, :NumberField(frame, _default, field_type=field_type, widget_options=kwargs),
            Color.__name__:lambda _default, **kwargs, :ColorField(frame, _default, widget_options=kwargs),
            Location.__name__: lambda _default, **kwargs, :LocationField(frame, _default, widget_options=kwargs),
        }
        return build_map[field_type.__name__](default, **kwargs)

    @classmethod
    def executable(cls, method):
        parameters = dict(
            inspect.signature(
                method
            ).parameters
        )
        if 'self' in parameters:
            del parameters['self'] # don't need to configure this...
        for name, field in parameters.items():
            if (field.annotation not in cls.buildable_types and
                field.default.__class__ not in cls.buildable_types):
                return False

        return True


    @property
    def values(self):
        values = dict()
        try:
            if self._fields:
                self.show()
            if self.cancelled:
                return None
        except:
            return None
        finally:
            for name, field in self._fields.items():
                values[name] = field.value
        return values

    def cancel(self):
        self.cancelled=True
        self.hide()

    def hide(self):
        self.wm_withdraw()
        self._finished = True
        self.initial_focus = None
        tk.Toplevel.destroy(self)
        self._parent_window.focus_set()

    def show(self, **options):
        self.wm_deiconify()
        while not self._finished:
            self.update()
            self.update_idletasks()

    def evaluate(self):
        try:
            value = self._method(**self.values)
            return value
        except:
            return None


class InstanceBuilder(FunctionCaller):

    _object_type:type

    def __init__(self, parent:tk.Toplevel, instance_type: type):
        self._object_type = instance_type
        super().__init__(parent, instance_type.__init__)
        self.wm_title(instance_type.__name__)
        self.field_frame.config(text=instance_type.__name__)

    @staticmethod
    def can_init_pure_default(_cls:type):
        parameters = dict(
            inspect.signature(
                _cls.__init__
            ).parameters
        )
        if parameters.get('self') is not None:
            del parameters['self'] # this will never have a default, but we don't need it
        for name, param in parameters.items():
            if param.default is inspect.Parameter.empty:
                return False

        return True

    def evaluate(self):
        try:
            instance = self._object_type(**self.values)
            return instance
        except:
            return None
