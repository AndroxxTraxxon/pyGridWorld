import tkinter as tk
from threading import Timer
import pyGridWorld.world as world


class WorldFrame(tk.Frame):

    control:"GUIController"
    display:"GridPanel"
    messageArea:tk.Message
    menuItemsDisabledDuringRun: list
    world: world.World
    def __init__(self, root:tk.Tk=None):
        if root is None:
            root = tk.Tk()
        self.root = root

    def repaint(self):
        pass


class GridPanel(tk.Frame):
    pass

class DisplayMap:
    pass

class GUIController:
    INDEFINITE, FIXED_STEPS, PROMPT_STEPS = 0, 1, 2
    MIN_DELAY_MSECS, MAX_DELAY_MSECS = 10, 1000
    INITIAL_DELAY = MIN_DELAY_MSECS + (MAX_DELAY_MSECS - MIN_DELAY_MSECS) / 2

    tip_timer:Timer = None
    step_button: tk.Button = None
    run_bitton: tk.Button = None
    stop_button: tk.Button = None

    control_panel: tk.Frame = None
    display: GridPanel = None
    parent_frame: WorldFrame = None
    num_steps_to_run: int = None
    num_steps_so_far: int = None
    resources: dict = None
    display_map: DisplayMap = None
    running: bool = None
    occupant_classes: set = None

    def __init__(self, parent:WorldFrame, disp:GridPanel, display_map:DisplayMap, res:dict):
        self.resources = res
        self.display = disp
        self.parent_frame = parent
        self.display_map = display_map
        self.makeControls()
        
        self.occupant_classes = set()

        world = self.parent_frame.world


    def makeControls(self):
        pass

    

    