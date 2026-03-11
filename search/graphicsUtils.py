"""
Graphics utilities for Pacman visualization.

This module provides a simple graphics framework built on tkinter for:
- Creating and managing a graphics window
- Drawing basic shapes (polygons, circles, text)
- Handling keyboard and mouse input
- Managing animation timing

Updates:
    9 Nov 2024 (George Rudolph):
    - Added comprehensive type hints throughout
    - Improved docstrings with Args/Returns/Note sections
    - Made global variables explicitly typed
    - Added error handling
    - Organized code into logical sections
    - Refactored test code into test_draw_ghost() function
    - Maintained compatibility with existing codebase

Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

import sys
import math
import random
import string
import time
import types
import tkinter
import os.path
from typing import Any, List, Optional, Tuple, Union, Callable

# Platform check
_Windows = sys.platform == 'win32'

# Graphics globals
_root_window: Optional[tkinter.Tk] = None      # The root window for graphics output
_canvas: Optional[tkinter.Canvas] = None      # The canvas which holds graphics
_canvas_xs: Optional[int] = None      # Size of canvas object
_canvas_ys: Optional[int] = None
_canvas_x: Optional[float] = None      # Current position on canvas
_canvas_y: Optional[float] = None
_canvas_col: Optional[str] = None      # Current colour (set to black below)
_canvas_tsize: int = 12
_canvas_tserifs: int = 0

def formatColor(r: float, g: float, b: float) -> str:
    """
    Convert RGB values to a hex color string.
    
    Args:
        r: Red component (0-1)
        g: Green component (0-1)
        b: Blue component (0-1)
        
    Returns:
        Hex color string (e.g., '#FF0000' for red)
    """
    return f'#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}'

def colorToVector(color: str) -> List[float]:
    """
    Convert a hex color string to RGB values.
    
    Args:
        color: Hex color string (e.g., '#FF0000')
        
    Returns:
        List of [r, g, b] values (0-1)
    """
    return [int(color[i:i+2], 16) / 256.0 for i in (1, 3, 5)]

# Font selection based on platform
if _Windows:
    _canvas_tfonts = ['times new roman', 'lucida console']
else:
    _canvas_tfonts = ['times', 'lucidasans-24']

def sleep(secs: float) -> None:
    """
    Pause the program for the specified duration.
    
    Args:
        secs: Number of seconds to pause
        
    Note:
        Uses tkinter's event loop if graphics are active, otherwise uses time.sleep
    """
    if _root_window is None:
        time.sleep(secs)
    else:
        _root_window.update_idletasks()
        _root_window.after(int(1000 * secs), _root_window.quit)
        _root_window.mainloop()

def begin_graphics(width: int = 640, height: int = 480, 
                  color: str = formatColor(0, 0, 0), title: Optional[str] = None) -> None:
    """
    Initialize a graphics window with specified parameters.
    
    Args:
        width: Window width in pixels (default: 640)
        height: Window height in pixels (default: 480)
        color: Background color (default: black)
        title: Window title (default: 'Graphics Window')
        
    Note:
        Creates global window and canvas objects for other graphics functions
    """
    global _root_window, _canvas, _canvas_x, _canvas_y, _canvas_xs, _canvas_ys, _bg_color

    # Check for duplicate call
    if _root_window is not None:
        # Lose the window.
        _root_window.destroy()

    # Save the canvas size parameters
    _canvas_xs, _canvas_ys = width - 1, height - 1
    _canvas_x, _canvas_y = 0, _canvas_ys
    _bg_color = color

    # Create the root window
    _root_window = tkinter.Tk()
    _root_window.protocol('WM_DELETE_WINDOW', _destroy_window)
    _root_window.title(title or 'Graphics Window')
    _root_window.resizable(0, 0)

    # Create the canvas object
    try:
        _canvas = tkinter.Canvas(_root_window, width=width, height=height)
        _canvas.pack()
        draw_background()
        _canvas.update()
    except Exception as e:
        _root_window = None
        raise e

    # Bind to key-down and key-up events
    _root_window.bind("<KeyPress>", _keypress)
    _root_window.bind("<KeyRelease>", _keyrelease)
    _root_window.bind("<FocusIn>", _clear_keys)
    _root_window.bind("<FocusOut>", _clear_keys)
    _root_window.bind("<Button-1>", _leftclick)
    _root_window.bind("<Button-2>", _rightclick)
    _root_window.bind("<Button-3>", _rightclick)
    _root_window.bind("<Control-Button-1>", _ctrl_leftclick)
    _clear_keys()

def draw_background() -> None:
    """
    Draw the background color on the canvas.
    
    Uses the global _bg_color and canvas dimensions.
    """
    corners = [(0, 0), (0, _canvas_ys), (_canvas_xs, _canvas_ys), (_canvas_xs, 0)]
    polygon(corners, _bg_color, fillColor=_bg_color, filled=True, smoothed=False)

def _destroy_window(event: Optional[tkinter.Event] = None) -> None:
    """
    Destroy the graphics window and exit the program.
    
    Args:
        event: Tkinter event (unused, but required for binding)
    """
    sys.exit(0)

def end_graphics() -> None:
    """
    Clean up window and graphics resources.
    
    Should be called when finished with all graphics operations.
    """
    global _root_window, _canvas, _mouse_enabled
    try:
        try:
            sleep(1)
            if _root_window is not None:
                _root_window.destroy()
        except SystemExit as e:
            print('Ending graphics raised an exception:', e)
    finally:
        _root_window = None
        _canvas = None
        _mouse_enabled = 0
        _clear_keys()

def clear_screen(background: Optional[str] = None) -> None:
    """
    Clear the graphics window.
    
    Args:
        background: Optional new background color
    """
    global _canvas_x, _canvas_y
    _canvas.delete('all')
    draw_background()
    _canvas_x, _canvas_y = 0, _canvas_ys

def polygon(coords: List[Tuple[float, float]], outlineColor: str, 
            fillColor: Optional[str] = None, filled: int = 1, 
            smoothed: int = 1, behind: int = 0, width: int = 1) -> Any:
    """
    Draw a polygon on the canvas.
    
    Args:
        coords: List of (x,y) coordinates for polygon vertices
        outlineColor: Color string for polygon outline
        fillColor: Color string for polygon interior (default: same as outline)
        filled: Boolean indicating if polygon should be filled (default: True)
        smoothed: Boolean indicating if polygon should be smoothed (default: True)
        behind: Number of layers to push polygon back (default: 0)
        width: Width of polygon outline (default: 1)
        
    Returns:
        Canvas polygon object
    """
    c = []
    for coord in coords:
        c.append(coord[0])
        c.append(coord[1])
    if fillColor is None: 
        fillColor = outlineColor
    if filled == 0: 
        fillColor = ""
    poly = _canvas.create_polygon(c, outline=outlineColor, fill=fillColor, 
                                smooth=smoothed, width=width)
    if behind > 0:
        _canvas.tag_lower(poly, behind) # Higher should be more visible
    return poly

def square(pos: Tuple[float, float], r: float, color: str, 
           filled: int = 1, behind: int = 0) -> Any:
    """
    Draw a square on the canvas.
    
    Args:
        pos: (x,y) coordinates of square center
        r: Half-length of square side
        color: Color string for square
        filled: Boolean indicating if square should be filled (default: True)
        behind: Number of layers to push square back (default: 0)
        
    Returns:
        Canvas polygon object representing the square
    """
    x, y = pos
    coords = [(x - r, y - r), (x + r, y - r), 
             (x + r, y + r), (x - r, y + r)]
    return polygon(coords, color, color, filled, 0, behind=behind)

def circle(pos: Tuple[float, float], r: float, outlineColor: str, 
          fillColor: Optional[str] = None, endpoints: Optional[List[int]] = None, 
          style: str = 'pieslice', width: int = 2) -> Any:
    """
    Draw a circle/arc on the canvas.
    
    Args:
        pos: (x,y) coordinates of circle center
        r: Radius of circle
        outlineColor: Color string for circle outline
        fillColor: Color string for circle interior (default: same as outline)
        endpoints: List of [start,end] angles in degrees (default: [0,359])
        style: Style of circle ('pieslice', 'arc', etc.) (default: 'pieslice')
        width: Width of circle outline (default: 2)
        
    Returns:
        Canvas arc object
    """
    x, y = pos
    x0, x1 = x - r - 1, x + r
    y0, y1 = y - r - 1, y + r
    if endpoints is None:
        e = [0, 359]
    else:
        e = list(endpoints)
    while e[0] > e[1]: 
        e[1] = e[1] + 360

    return _canvas.create_arc(x0, y0, x1, y1, outline=outlineColor, 
                            fill=fillColor or outlineColor,
                            extent=e[1] - e[0], start=e[0], 
                            style=style, width=width)

def image(pos: Tuple[float, float], file: str = "../../blueghost.gif") -> Any:
    """
    Draw an image on the canvas.
    
    Args:
        pos: (x,y) coordinates for image placement
        file: Path to image file (default: "../../blueghost.gif")
        
    Returns:
        Canvas image object
    """
    x, y = pos
    return _canvas.create_image(x, y, image=tkinter.PhotoImage(file=file), 
                              anchor=tkinter.NW)

def refresh() -> None:
    """
    Update the canvas display.
    
    Forces any pending draw operations to be displayed.
    """
    _canvas.update_idletasks()

def moveCircle(id: Any, pos: Tuple[float, float], r: float, 
               endpoints: Optional[List[int]] = None) -> None:
    """
    Move a circle/arc to a new position.
    
    Args:
        id: Canvas object ID of circle to move
        pos: New (x,y) coordinates for circle center
        r: Radius of circle
        endpoints: Optional list of [start,end] angles in degrees
    """
    global _canvas_x, _canvas_y
    
    x, y = pos
    x0, x1 = x - r - 1, x + r
    y0, y1 = y - r - 1, y + r
    if endpoints is None:
        e = [0, 359]
    else:
        e = list(endpoints)
    while e[0] > e[1]: 
        e[1] = e[1] + 360

    if os.path.isfile('flag'):
        edit(id, ('extent', e[1] - e[0]))
    else:
        edit(id, ('start', e[0]), ('extent', e[1] - e[0]))
    move_to(id, x0, y0)

def edit(id: Any, *args: Tuple[str, Any]) -> None:
    """
    Edit the properties of a canvas object.
    
    Args:
        id: Canvas object ID to edit
        *args: Tuples of (property_name, new_value)
    """
    _canvas.itemconfigure(id, **dict(args))

def text(pos: Tuple[float, float], color: str, contents: str, 
         font: str = 'Helvetica', size: int = 12, 
         style: str = 'normal', anchor: str = "nw") -> Any:
    """
    Draw text on the canvas.
    
    Args:
        pos: (x,y) coordinates for text placement
        color: Color string for text
        contents: String to display
        font: Font family to use (default: 'Helvetica')
        size: Font size (default: 12)
        style: Font style (default: 'normal')
        anchor: Text anchor point (default: "nw")
        
    Returns:
        Canvas text object
    """
    global _canvas_x, _canvas_y
    x, y = pos
    font = (font, str(size), style)
    return _canvas.create_text(x, y, fill=color, text=contents, 
                             font=font, anchor=anchor)

def changeText(id: Any, newText: str, font: Optional[str] = None, 
               size: int = 12, style: str = 'normal') -> None:
    """
    Change the text of an existing text object.
    
    Args:
        id: Canvas object ID of text to change
        newText: New string to display
        font: Optional new font family
        size: New font size (default: 12)
        style: New font style (default: 'normal')
    """
    _canvas.itemconfigure(id, text=newText)
    if font is not None:
        _canvas.itemconfigure(id, font=(font, f'-{size}', style))

def changeColor(id: Any, newColor: str) -> None:
    """
    Change the color of an existing canvas object.
    
    Args:
        id: Canvas object ID to modify
        newColor: New color string
    """
    _canvas.itemconfigure(id, fill=newColor)

def line(here: Tuple[float, float], there: Tuple[float, float], 
         color: str = formatColor(0, 0, 0), width: int = 2) -> Any:
    """
    Draw a line between two points.
    
    Args:
        here: Starting (x,y) coordinates
        there: Ending (x,y) coordinates
        color: Color string for line (default: black)
        width: Line width (default: 2)
        
    Returns:
        Canvas line object
    """
    x0, y0 = here[0], here[1]
    x1, y1 = there[0], there[1]
    return _canvas.create_line(x0, y0, x1, y1, fill=color, width=width)

def move_to(object: Any, x: float, y: Optional[float] = None,
            d_o_e: Callable = lambda arg: _root_window.dooneevent(arg),
            d_w: int = tkinter._tkinter.DONT_WAIT) -> None:
    """
    Move an object to absolute coordinates.
    
    Args:
        object: Canvas object ID to move
        x: New x coordinate or (x,y) tuple
        y: New y coordinate (if x is not a tuple)
        d_o_e: Event handler function (default: dooneevent)
        d_w: Wait flag (default: DONT_WAIT)
    """
    if y is None:
        try: 
            x, y = x
        except: 
            raise Exception('incomprehensible coordinates')

    horiz = True
    newCoords = []
    current_x, current_y = _canvas.coords(object)[0:2] # first point
    for coord in _canvas.coords(object):
        if horiz:
            inc = x - current_x
        else:
            inc = y - current_y
        horiz = not horiz

        newCoords.append(coord + inc)

    _canvas.coords(object, *newCoords)
    d_o_e(d_w)

def move_by(object: Any, x: float, y: Optional[float] = None,
            d_o_e: Callable = lambda arg: _root_window.dooneevent(arg),
            d_w: int = tkinter._tkinter.DONT_WAIT, 
            lift: bool = False) -> None:
    """
    Move an object by a relative offset.
    
    Args:
        object: Canvas object ID to move
        x: X offset or (x,y) tuple
        y: Y offset (if x is not a tuple)
        d_o_e: Event handler function (default: dooneevent)
        d_w: Wait flag (default: DONT_WAIT)
        lift: Whether to lift object to top (default: False)
    """
    if y is None:
        try: 
            x, y = x
        except: 
            raise Exception('incomprehensible coordinates')

    horiz = True
    newCoords = []
    for coord in _canvas.coords(object):
        if horiz:
            inc = x
        else:
            inc = y
        horiz = not horiz

        newCoords.append(coord + inc)

    _canvas.coords(object, *newCoords)
    d_o_e(d_w)
    if lift:
        _canvas.tag_raise(object)

def writePostscript(filename: str) -> None:
    """
    Write the current canvas to a postscript file.
    
    Args:
        filename: Name of the file to write to
    """
    with open(filename, 'w') as psfile:
        psfile.write(_canvas.postscript(pageanchor='sw',
                                      y='0.c',
                                      x='0.c'))

def remove_from_screen(x: Any,
                      d_o_e: Callable = lambda arg: _root_window.dooneevent(arg),
                      d_w: int = tkinter._tkinter.DONT_WAIT) -> None:
    """
    Remove an object from the canvas.
    
    Args:
        x: Canvas object ID to remove
        d_o_e: Event handler function (default: dooneevent)
        d_w: Wait flag (default: DONT_WAIT)
    """
    _canvas.delete(x)
    d_o_e(d_w)

def _adjust_coords(coord_list: List[float], x: float, y: float) -> List[float]:
    """
    Adjust coordinates by adding an offset.
    
    Args:
        coord_list: List of coordinates to adjust
        x: X offset to add
        y: Y offset to add
        
    Returns:
        List of adjusted coordinates
    """
    for i in range(0, len(coord_list), 2):
        coord_list[i] = coord_list[i] + x
        coord_list[i + 1] = coord_list[i + 1] + y
    return coord_list

##############################################################################
### Keyboard handling ########################################################
##############################################################################

# We bind to key-down and key-up events.
_keysdown: dict = {}
_keyswaiting: dict = {}
# This holds an unprocessed key release. We delay key releases by up to
# one call to keys_pressed() to get round a problem with auto repeat.
_got_release: Optional[bool] = None

def _keypress(event: tkinter.Event) -> None:
    """
    Internal handler for key press events.
    
    Args:
        event: Tkinter key event
    """
    global _got_release
    #remap_arrows(event)
    _keysdown[event.keysym] = 1
    _keyswaiting[event.keysym] = 1
    _got_release = None

def _keyrelease(event: tkinter.Event) -> None:
    """
    Internal handler for key release events.
    
    Args:
        event: Tkinter key event
    """
    global _got_release
    #remap_arrows(event)
    try:
        del _keysdown[event.keysym]
    except:
        pass
    _got_release = True

def remap_arrows(event: tkinter.Event) -> None:
    """
    Remap arrow keys to WASD.
    
    Args:
        event: Tkinter key event
        
    Note:
        This is intended for keyboard agents but currently disabled.
    """
    # TURN ARROW PRESSES INTO LETTERS (SHOULD BE IN KEYBOARD AGENT)
    if event.char in ['a', 's', 'd', 'w']:
        return
    if event.keycode in [37, 101]: # LEFT ARROW (win / x)
        event.char = 'a'
    if event.keycode in [38, 99]: # UP ARROW
        event.char = 'w'
    if event.keycode in [39, 102]: # RIGHT ARROW
        event.char = 'd'
    if event.keycode in [40, 104]: # DOWN ARROW
        event.char = 's'

def _clear_keys(event: Optional[tkinter.Event] = None) -> None:
    """
    Clear all key states.
    
    Args:
        event: Optional Tkinter event (unused but required for binding)
    """
    global _keysdown, _got_release, _keyswaiting
    _keysdown = {}
    _keyswaiting = {}
    _got_release = None

def keys_pressed(d_o_e: Callable = lambda arg: _root_window.dooneevent(arg),
                d_w: int = tkinter._tkinter.DONT_WAIT) -> List[str]:
    """
    Return list of keys currently pressed.
    
    Args:
        d_o_e: Event handler function (default: dooneevent)
        d_w: Wait flag (default: DONT_WAIT)
        
    Returns:
        List of key symbols currently pressed
    """
    d_o_e(d_w)
    if _got_release:
        d_o_e(d_w)
    return list(_keysdown.keys())

def keys_waiting() -> List[str]:
    """
    Return list of keys that have been pressed since last check.
    
    Returns:
        List of key symbols pressed since last call
        
    Note:
        Keys are removed from waiting list after being returned
    """
    global _keyswaiting
    keys = list(_keyswaiting.keys())
    _keyswaiting = {}
    return keys

def wait_for_keys() -> List[str]:
    """
    Wait for user to press a key and return all keys pressed.
    
    Returns:
        List of key symbols pressed
    """
    keys: List[str] = []
    while not keys:
        keys = keys_pressed()
        sleep(0.05)
    return keys

##############################################################################
### Mouse handling ##########################################################
##############################################################################

_leftclick_loc: Optional[Tuple[int, int]] = None
_rightclick_loc: Optional[Tuple[int, int]] = None
_ctrl_leftclick_loc: Optional[Tuple[int, int]] = None

def _leftclick(event: tkinter.Event) -> None:
    """Handle left click events."""
    global _leftclick_loc
    _leftclick_loc = (event.x, event.y)

def _rightclick(event: tkinter.Event) -> None:
    """Handle right click events."""
    global _rightclick_loc
    _rightclick_loc = (event.x, event.y)

def _ctrl_leftclick(event: tkinter.Event) -> None:
    """Handle ctrl-left click events."""
    global _ctrl_leftclick_loc
    _ctrl_leftclick_loc = (event.x, event.y)

def wait_for_click() -> Tuple[Tuple[int, int], str]:
    """
    Wait for a mouse click and return click location and type.
    
    Returns:
        Tuple of ((x,y), click_type) where click_type is one of:
        'left', 'right', or 'ctrl_left'
    """
    while True:
        global _leftclick_loc
        global _rightclick_loc
        global _ctrl_leftclick_loc
        if _leftclick_loc is not None:
            val = _leftclick_loc
            _leftclick_loc = None
            return val, 'left'
        if _rightclick_loc is not None:
            val = _rightclick_loc
            _rightclick_loc = None
            return val, 'right'
        if _ctrl_leftclick_loc is not None:
            val = _ctrl_leftclick_loc
            _ctrl_leftclick_loc = None
            return val, 'ctrl_left'
        sleep(0.05)

def test_draw_ghost() -> None:
    """
    Test the graphics module by drawing a ghost shape and a circle.
    
    Creates a window, draws a white ghost shape, moves it,
    and adds an orange circle with partial endpoints.
    """
    begin_graphics()
    clear_screen()
    ghost_shape = [(x * 10 + 20, y * 10 + 20) for x, y in [
        (0, -0.5),
        (0.25, -0.75),
        (0.5, -0.5),
        (0.75, -0.75),
        (0.75, 0.5),
        (0.5, 0.75),
        (-0.5, 0.75),
        (-0.75, 0.5),
        (-0.75, -0.75),
        (-0.5, -0.5),
        (-0.25, -0.75)
    ]]
    ghost = polygon(ghost_shape, formatColor(1, 1, 1))
    move_to(ghost, (50, 50))
    circle((150, 150), 20, formatColor(0.7, 0.3, 0.0), endpoints=[15, -15])
    sleep(2)

if __name__ == '__main__':
    test_draw_ghost()