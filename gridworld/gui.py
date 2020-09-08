
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

    # private variables
    __needs_render:bool

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
            if self.control.running:
                self.control.stop()
            exit()
        
    def mainloop(self):
        while self.running:
            while not self.ui_update_actions.empty():
                action_func = self.ui_update_actions.get()
                action_func()
            if self.__needs_render:
                self.display.render()
            self.update()
            self.update_idletasks()
            sleep(0.01)

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
        view_menu.add_command(label="Edit", command=self.display.edit_location)
        view_menu.add_command(label="Delete", command=self.display.delete_location)
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

    def configure_grid_type(self, grid_type:type):
        def action():
            instance = InstanceBuilder(self, grid_type).evaluate()
            if isinstance(instance, grid_type):
                self.set_grid(instance)
        return action

    def set_grid(self, new_grid:Grid):
        old_grid = self.world.grid
        occupants = dict()
        for loc in tuple(old_grid.occupiedLocations):
            occupants[loc] = self.world.remove(loc)
            
        self.world.grid = new_grid
        self.display.grid = new_grid
        for loc, occupant in occupants.items():
            if new_grid.isValid(loc):
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
    TAG_OCCUPANTS='occ'
    TAG_GRID='grid'

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
    line_width:int
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
        self.line_width = self.DEFAULT_BORDER_WIDTH
        self.current_location = Location(0,0)
        self.image_sources = dict()
        self.used_images = dict()
        self.grid = parent.world.grid
        width = self.num_cols * (self.cell_size + self.line_width)
        height = self.num_rows * (self.cell_size + self.line_width)
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
        self.render(True)
        self.canvas.bind('<Button-1>', self.handle_click)
        self.canvas.bind('<Button-3>', self.handle_click)
        self.canvas.bind('<Return>', self.show_location_menu)
        self.canvas.bind('<space>', lambda event: parent.world.step())
        self.focus_set()

    @property
    def grid(self) -> Grid:
        return self._grid

    @grid.setter
    def grid(self, grid:Grid):
        try:
            self._grid = grid
            self.num_cols = self.grid.colCount
            self.num_rows = self.grid.rowCount
        except:
            self.num_cols = self.DEFAULT_CELL_COUNT
            self.num_rows = self.DEFAULT_CELL_COUNT

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

    def render(self, draw_grid=False):
        width = self.num_cols * (self.cell_size + self.line_width)
        height = self.num_rows * (self.cell_size + self.line_width)

        if draw_grid:
            self.canvas.create_rectangle(
                0,0, 
                width,height, 
                fill=str(Color.WHITE),
                width=self.line_width
            )
            self.drawGridLines()
            self.drawCurrentLocation()

        self.canvas.delete(self.TAG_OCCUPANTS)
        self.drawOccupants()

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
        for loc in self.grid.occupiedLocations:
            occupant = self.grid.get(loc)
            if occupant is not None:
                xleft = (self.cell_size + self.line_width) * loc.col + 1
                ytop = (self.cell_size + self.line_width) * loc.row + 1
                self.drawOccupant(xleft, ytop, occupant)

    def drawOccupant(self, xleft:int, ytop:int, occupant):
        image = None
        if occupant.image_description in self.used_images:
            image = self.used_images.get(occupant.image_description)
        else:
            image = self.generate_image(occupant)
            self.used_images[occupant.image_description] = image
        if image is not None:
            self.canvas.create_image(
                int(xleft + self.cell_size/2), 
                int(ytop + self.cell_size/2), 
                image=image,
                anchor=tk.CENTER,
                tags=self.TAG_OCCUPANTS
                )
        else:
            self.canvas.create_text(
                xleft, 
                ytop, 
                text=occupant.__class__.__name__,
                anchor=tk.NW,
                tags=self.TAG_OCCUPANTS
            )

    def generate_image(self, occupant):
        image = self.get_source_image(occupant.__class__.__name__)
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

    def get_source_image(self, name):
        if name in self.image_sources:
            return self.image_sources.get(name).copy()
        path = _search_for_image(name)
        if path is None:
            return None
        image = Image.open(path)
        maxsize = (480, 480)
        image.thumbnail(maxsize, Image.ANTIALIAS) # no need for the images to be huge. crop this down.
        self.image_sources[name] = image
        return image.copy()

    def drawCurrentLocation(self):
        row = self.current_location.row
        col = self.current_location.col
        self.canvas.create_rectangle(
            (self.cell_size + self.line_width) * col,
            (self.cell_size + self.line_width) * row,
            (self.cell_size + self.line_width) * (col+1),
            (self.cell_size + self.line_width) * (row+1),
            width=self.line_width+1,
            tags=self.TAG_GRID
        )

    def recalculateCellSize(self, min_size=MIN_CELL_SIZE):
        pass

    def handle_click(self, event):
        print('Canvas clicked!', event.x, event.y)

    def show_location_menu(self, event):
        print('Showing Location Menu!')

    def move_location(self, dr, dc):
        new_location = Location(
            self.current_location.row + dr,
            self.current_location.col + dc,
        )
        if self.grid.isValid(new_location):
            self.current_location = new_location

    def edit_location(self):
        pass

    def delete_location(self):
        pass

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
        self.occupant_classes = list()
        self.delay_time = tk.IntVar()
        self.delay_time.set(self.INITIAL_DELAY)
        self.__make_controls()
        self.num_steps_to_run = 0
        self.num_steps_so_far = 0
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

    def __update_delay_time(self, delay):
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
        self.options.append(self._rand_key)
        self._widget = tk.OptionMenu(parent_widget, self._var, *self.options)

    @property
    def value(self) -> Color:
        str_value = self._var.get()
        if str_value is self._rand_key:
            return Color.random()
        else:
            return self.options[str_value]

class FunctionCaller(tk.Toplevel):

    _parent_window:tk.Toplevel
    _method: type
    _fields:dict
    _finished: bool

    def __init__(self, parent:tk.Toplevel, method:type):
        self.cancelled = False
        super().__init__(parent, padx=5, pady=5)
        self.wm_withdraw()
        self._parent_window = parent
        self._method = method
        self.wm_protocol('WM_DELETE_WINDOW', self.cancel)
        self._finished = False
        self._build_fields()
        self.wm_title(method.__name__)
        button_frame = tk.Frame(self)
        confirm_button = tk.Button(button_frame, text='Confirm', command=self.hide)
        confirm_button.pack(side=tk.LEFT)
        cancel_button = tk.Button(button_frame, text='Cancel', command=self.cancel)
        cancel_button.pack(side=tk.RIGHT)
        button_frame.pack(side=tk.TOP, fill=tk.X)

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
            frame = tk.Frame(self)
            field_type = param.annotation
            field_default = None
            if field_type is inspect.Parameter.empty:
                if param.default is inspect.Parameter.empty:
                    raise NotImplementedError(
                'Inspected Classes must mark their __init__ methods with type annotations or ' 
                'default values'
                )
                field_type = type(param)
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
        }
        return build_map[field_type.__name__](default, **kwargs)

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

    def evaluate(self):
        try:
            instance = self._object_type(**self.values)
            return instance
        except:
            return None
