"""
# graphicsUtils.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

Graphics utilities module for the Pacman game.

This module provides a comprehensive set of graphics utilities using tkinter for:
1. Creating and managing a graphics window with configurable dimensions
2. Drawing primitive shapes (polygons, circles, lines, text)
3. Handling keyboard and mouse input events
4. Managing animations and screen updates with timing control
5. Color management and conversion utilities

The module uses tkinter for all graphics operations and provides a simplified,
high-level interface for the rest of the game code to use. It handles all the
low-level graphics details while exposing clean, easy-to-use drawing functions.

Changes by George Rudolph 30 Nov 2024:
- Verified compatibility with Python 3.13
- Enhanced module documentation
- Added type hints throughout
- Improved error handling
- Added input validation
- Modernized color handling
"""

import sys
import math
import random
import string
import time
import types
import tkinter
import os.path
from typing import List, Tuple, Optional, Union, Any, Dict, Set

_Windows = sys.platform == "win32"  # True if on Win95/98/NT

_root_window = None  # The root window for graphics output
_canvas = None  # The canvas which holds graphics
_canvas_xs = None  # Size of canvas object
_canvas_ys = None
_canvas_x = None  # Current position on canvas
_canvas_y = None
_canvas_col = None  # Current colour (set to black below)
_canvas_tsize = 12
_canvas_tserifs = 0


def formatColor(r: float, g: float, b: float) -> str:
    """Convert RGB values to hex color string.
    
    Args:
        r: Red value between 0 and 1
        g: Green value between 0 and 1 
        b: Blue value between 0 and 1
        
    Returns:
        Hex color string in format '#RRGGBB'
    """
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def colorToVector(color: str) -> List[float]:
    """Convert hex color string to RGB values.
    
    Args:
        color: Hex color string in format '#RRGGBB'
        
    Returns:
        List of RGB values between 0 and 1
    """
    return list(map(lambda x: int(x, 16) / 256.0, [color[1:3], color[3:5], color[5:7]]))


if _Windows:
    _canvas_tfonts = ["times new roman", "lucida console"]
else:
    _canvas_tfonts = ["times", "lucidasans-24"]
    pass  # XXX need defaults here


def sleep(secs: float) -> None:
    """Pause execution for specified number of seconds.
    
    Args:
        secs: Number of seconds to sleep
        
    If running in graphics mode, updates the display during sleep.
    """
    global _root_window
    if _root_window == None:
        time.sleep(secs)
    else:
        _root_window.update_idletasks()
        _root_window.after(int(1000 * secs), _root_window.quit)
        _root_window.mainloop()


def begin_graphics(width: int = 640, height: int = 480, color: str = formatColor(0, 0, 0), title: Optional[str] = None) -> None:
    """Initialize the graphics window.
    
    Args:
        width: Width of window in pixels
        height: Height of window in pixels  
        color: Background color as hex string
        title: Window title string
        
    Creates the root window and canvas, sets up event bindings.
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
    _root_window.protocol("WM_DELETE_WINDOW", _destroy_window)
    _root_window.title(title or "Graphics Window")
    _root_window.resizable(0, 0)

    # Create the canvas object
    try:
        _canvas = tkinter.Canvas(_root_window, width=width, height=height)
        _canvas.pack()
        draw_background()
        _canvas.update()
    except:
        _root_window = None
        raise

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


_leftclick_loc = None
_rightclick_loc = None
_ctrl_leftclick_loc = None


def _leftclick(event: tkinter.Event) -> None:
    global _leftclick_loc
    _leftclick_loc = (event.x, event.y)


def _rightclick(event: tkinter.Event) -> None:
    global _rightclick_loc
    _rightclick_loc = (event.x, event.y)


def _ctrl_leftclick(event: tkinter.Event) -> None:
    global _ctrl_leftclick_loc
    _ctrl_leftclick_loc = (event.x, event.y)


def wait_for_click() -> Tuple[Tuple[int, int], str]:
    """Wait for and return the next mouse click.
    
    Returns:
        Tuple of ((x,y), click_type) where click_type is 'left', 'right' or 'ctrl_left'
    """
    while True:
        global _leftclick_loc
        global _rightclick_loc
        global _ctrl_leftclick_loc
        if _leftclick_loc != None:
            val = _leftclick_loc
            _leftclick_loc = None
            return val, "left"
        if _rightclick_loc != None:
            val = _rightclick_loc
            _rightclick_loc = None
            return val, "right"
        if _ctrl_leftclick_loc != None:
            val = _ctrl_leftclick_loc
            _ctrl_leftclick_loc = None
            return val, "ctrl_left"
        sleep(0.05)


def draw_background() -> None:
    """Draw the background color filling the entire canvas."""
    corners = [(0, 0), (0, _canvas_ys), (_canvas_xs, _canvas_ys), (_canvas_xs, 0)]
    polygon(corners, _bg_color, fillColor=_bg_color, filled=True, smoothed=False)


def _destroy_window(event: Optional[tkinter.Event] = None) -> None:
    """Handle window close event by exiting program."""
    sys.exit(0)


#    global _root_window
#    _root_window.destroy()
#    _root_window = None
# print "DESTROY"


def end_graphics() -> None:
    """Clean up window and graphics resources."""
    global _root_window, _canvas, _mouse_enabled
    try:
        try:
            sleep(1)
            if _root_window != None:
                _root_window.destroy()
        except SystemExit as e:
            print(f"Ending graphics raised an exception: {e}")
    finally:
        _root_window = None
        _canvas = None
        _mouse_enabled = 0
        _clear_keys()


def clear_screen(background: Optional[str] = None) -> None:
    """Clear the graphics canvas.
    
    Args:
        background: Optional background color to use
    """
    global _canvas_x, _canvas_y
    _canvas.delete("all")
    draw_background()
    _canvas_x, _canvas_y = 0, _canvas_ys


def polygon(
    coords: List[Tuple[float, float]], 
    outlineColor: str,
    fillColor: Optional[str] = None,
    filled: int = 1,
    smoothed: int = 1,
    behind: int = 0,
    width: int = 1
) -> int:
    """Draw a polygon on the canvas.
    
    Args:
        coords: List of (x,y) coordinates defining polygon vertices
        outlineColor: Color string for polygon outline
        fillColor: Optional color string for polygon fill
        filled: Whether to fill the polygon (1) or not (0)
        smoothed: Whether to smooth the polygon edges
        behind: Z-order value - higher numbers are more visible
        width: Width of polygon outline
        
    Returns:
        ID of the created polygon
    """
    c = []
    for coord in coords:
        c.append(coord[0])
        c.append(coord[1])
    if fillColor == None:
        fillColor = outlineColor
    if filled == 0:
        fillColor = ""
    poly = _canvas.create_polygon(
        c, outline=outlineColor, fill=fillColor, smooth=smoothed, width=width
    )
    if behind > 0:
        _canvas.tag_lower(poly, behind)  # Higher should be more visible
    return poly


def square(pos: Tuple[float, float], r: float, color: str, filled: int = 1, behind: int = 0) -> int:
    """Draw a square on the canvas.
    
    Args:
        pos: (x,y) coordinates of square center
        r: Half-length of square sides
        color: Color string for square
        filled: Whether to fill the square (1) or not (0)
        behind: Z-order value - higher numbers are more visible
        
    Returns:
        ID of the created square
    """
    x, y = pos
    coords = [(x - r, y - r), (x + r, y - r), (x + r, y + r), (x - r, y + r)]
    return polygon(coords, color, color, filled, 0, behind=behind)


def circle(
    pos: Tuple[float, float],
    r: float,
    outlineColor: str,
    fillColor: str,
    endpoints: Optional[Tuple[float, float]] = None,
    style: str = "pieslice",
    width: int = 2
) -> int:
    """Draw a circle/arc on the canvas.
    
    Args:
        pos: (x,y) coordinates of circle center
        r: Circle radius
        outlineColor: Color string for circle outline
        fillColor: Color string for circle fill
        endpoints: Optional (start,end) angles in degrees
        style: Style of arc ("pieslice", "arc", "chord")
        width: Width of circle outline
        
    Returns:
        ID of the created circle/arc
    """
    x, y = pos
    x0, x1 = x - r - 1, x + r
    y0, y1 = y - r - 1, y + r
    if endpoints == None:
        e = [0, 359]
    else:
        e = list(endpoints)
    while e[0] > e[1]:
        e[1] = e[1] + 360

    return _canvas.create_arc(
        x0,
        y0,
        x1,
        y1,
        outline=outlineColor,
        fill=fillColor,
        extent=e[1] - e[0],
        start=e[0],
        style=style,
        width=width,
    )


def image(pos: Tuple[float, float], file: str = "../../blueghost.gif") -> int:
    """Draw an image on the canvas.
    
    Args:
        pos: (x,y) coordinates for image placement
        file: Path to image file
        
    Returns:
        ID of the created image
    """
    x, y = pos
    # img = PhotoImage(file=file)
    return _canvas.create_image(
        x, y, image=tkinter.PhotoImage(file=file), anchor=tkinter.NW
    )


def refresh() -> None:
    """Update the canvas display."""
    _canvas.update_idletasks()


def moveCircle(id: int, pos: Tuple[float, float], r: float, endpoints: Optional[Tuple[float, float]] = None) -> None:
    """Move a circle/arc to a new position.
    
    Args:
        id: ID of circle to move
        pos: New (x,y) center coordinates
        r: Circle radius
        endpoints: Optional new (start,end) angles
    """
    global _canvas_x, _canvas_y

    x, y = pos
    #    x0, x1 = x - r, x + r + 1
    #    y0, y1 = y - r, y + r + 1
    x0, x1 = x - r - 1, x + r
    y0, y1 = y - r - 1, y + r
    if endpoints == None:
        e = [0, 359]
    else:
        e = list(endpoints)
    while e[0] > e[1]:
        e[1] = e[1] + 360

    if os.path.isfile("flag"):
        edit(id, ("extent", e[1] - e[0]))
    else:
        edit(id, ("start", e[0]), ("extent", e[1] - e[0]))
    move_to(id, x0, y0)


def edit(id: int, *args: Tuple[str, Any]) -> None:
    """Edit the properties of a canvas object.
    
    Args:
        id: ID of object to edit
        *args: Sequence of (property, value) tuples
    """
    _canvas.itemconfigure(id, **dict(args))


def text(
    pos: Tuple[float, float],
    color: str,
    contents: str,
    font: str = "Helvetica",
    size: int = 12,
    style: str = "normal",
    anchor: str = "nw"
) -> int:
    """Draw text on the canvas.
    
    Args:
        pos: (x,y) coordinates for text placement
        color: Color string for text
        contents: The text string to display
        font: Font family name
        size: Font size
        style: Font style ("normal", "bold", "italic")
        anchor: Text anchor position
        
    Returns:
        ID of the created text
    """
    global _canvas_x, _canvas_y
    x, y = pos
    font = (font, str(size), style)
    return _canvas.create_text(
        x, y, fill=color, text=contents, font=font, anchor=anchor
    )


def changeText(id: int, newText: str, font: Optional[str] = None, size: int = 12, style: str = "normal") -> None:
    """Change the text of an existing text object.
    
    Args:
        id: ID of text object
        newText: New text string
        font: Optional new font family
        size: New font size
        style: New font style
    """
    _canvas.itemconfigure(id, text=newText)
    if font != None:
        _canvas.itemconfigure(id, font=(font, f"-{size}", style))


def changeColor(id: int, newColor: str) -> None:
    """Change the color of an existing canvas object.
    
    Args:
        id: ID of object
        newColor: New color string
    """
    _canvas.itemconfigure(id, fill=newColor)


def line(here: Tuple[float, float], there: Tuple[float, float], color: str = formatColor(0, 0, 0), width: int = 2) -> int:
    """Draw a line on the canvas.
    
    Args:
        here: Starting (x,y) coordinates
        there: Ending (x,y) coordinates
        color: Color string for line
        width: Line width
        
    Returns:
        ID of the created line
    """
    x0, y0 = here[0], here[1]
    x1, y1 = there[0], there[1]
    return _canvas.create_line(x0, y0, x1, y1, fill=color, width=width)


##############################################################################
### Keypress handling ########################################################
##############################################################################

# We bind to key-down and key-up events.

_keysdown = {}
_keyswaiting = {}
# This holds an unprocessed key release.  We delay key releases by up to
# one call to keys_pressed() to get round a problem with auto repeat.
_got_release = None


def _keypress(event: tkinter.Event) -> None:
    """Handle key press events."""
    global _got_release
    # remap_arrows(event)
    _keysdown[event.keysym] = 1
    _keyswaiting[event.keysym] = 1
    #    print event.char, event.keycode
    _got_release = None


def _keyrelease(event: tkinter.Event) -> None:
    """Handle key release events."""
    global _got_release
    # remap_arrows(event)
    try:
        del _keysdown[event.keysym]
    except:
        pass
    _got_release = 1


def remap_arrows(event: tkinter.Event) -> None:
    """Remap arrow keys to WASD."""
    # TURN ARROW PRESSES INTO LETTERS (SHOULD BE IN KEYBOARD AGENT)
    if event.char in ["a", "s", "d", "w"]:
        return
    if event.keycode in [37, 101]:  # LEFT ARROW (win / x)
        event.char = "a"
    if event.keycode in [38, 99]:  # UP ARROW
        event.char = "w"
    if event.keycode in [39, 102]:  # RIGHT ARROW
        event.char = "d"
    if event.keycode in [40, 104]:  # DOWN ARROW
        event.char = "s"


def _clear_keys(event: Optional[tkinter.Event] = None) -> None:
    """Clear all key states."""
    global _keysdown, _got_release, _keyswaiting
    _keysdown = {}
    _keyswaiting = {}
    _got_release = None


def keys_pressed(
    d_o_e: Any = lambda arg: _root_window.dooneevent(arg),
    d_w: int = tkinter._tkinter.DONT_WAIT
) -> Set[str]:
    """Return the set of keys currently pressed."""
    d_o_e(d_w)
    if _got_release:
        d_o_e(d_w)
    return _keysdown.keys()


def keys_waiting() -> Set[str]:
    """Return the set of keys that have been released since last check."""
    global _keyswaiting
    keys = _keyswaiting.keys()
    _keyswaiting = {}
    return keys


# Block for a list of keys...


def wait_for_keys() -> List[str]:
    """Wait for and return a list of keys pressed."""
    keys = []
    while keys == []:
        keys = keys_pressed()
        sleep(0.05)
    return keys


def remove_from_screen(
    x: int,
    d_o_e: Any = lambda arg: _root_window.dooneevent(arg),
    d_w: int = tkinter._tkinter.DONT_WAIT
) -> None:
    """Remove an object from the canvas.
    
    Args:
        x: ID of object to remove
    """
    _canvas.delete(x)
    d_o_e(d_w)


def _adjust_coords(coord_list: List[float], x: float, y: float) -> List[float]:
    """Adjust coordinates by an offset.
    
    Args:
        coord_list: List of coordinates
        x: X offset
        y: Y offset
        
    Returns:
        New list with adjusted coordinates
    """
    for i in range(0, len(coord_list), 2):
        coord_list[i] = coord_list[i] + x
        coord_list[i + 1] = coord_list[i + 1] + y
    return coord_list


def move_to(
    object: int,
    x: Union[float, Tuple[float, float]],
    y: Optional[float] = None,
    d_o_e: Any = lambda arg: _root_window.dooneevent(arg),
    d_w: int = tkinter._tkinter.DONT_WAIT,
) -> None:
    """Move an object to absolute coordinates.
    
    Args:
        object: ID of object to move
        x: New x coordinate or (x,y) tuple
        y: New y coordinate if x is not a tuple
    """
    if y is None:
        try:
            x, y = x
        except:
            raise "incomprehensible coordinates"

    horiz = True
    newCoords = []
    current_x, current_y = _canvas.coords(object)[0:2]  # first point
    for coord in _canvas.coords(object):
        if horiz:
            inc = x - current_x
        else:
            inc = y - current_y
        horiz = not horiz

        newCoords.append(coord + inc)

    _canvas.coords(object, *newCoords)
    d_o_e(d_w)


def move_by(
    object: int,
    x: Union[float, Tuple[float, float]],
    y: Optional[float] = None,
    d_o_e: Any = lambda arg: _root_window.dooneevent(arg),
    d_w: int = tkinter._tkinter.DONT_WAIT,
    lift: bool = False
) -> None:
    """Move an object by a relative offset.
    
    Args:
        object: ID of object to move
        x: X offset or (x,y) tuple
        y: Y offset if x is not a tuple
        lift: Whether to raise object to top
    """
    if y is None:
        try:
            x, y = x
        except:
            raise Exception("incomprehensible coordinates")

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
    """Write the current canvas to a postscript file.
    
    Args:
        filename: Name of file to write to
    """
    psfile = open(filename, "w")
    psfile.write(_canvas.postscript(pageanchor="sw", y="0.c", x="0.c"))
    psfile.close()


ghost_shape = [
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
    (-0.25, -0.75),
]

if __name__ == "__main__":
    begin_graphics()
    clear_screen()
    ghost_shape = [(x * 10 + 20, y * 10 + 20) for x, y in ghost_shape]
    g = polygon(ghost_shape, formatColor(1, 1, 1))
    move_to(g, (50, 50))
    circle((150, 150), 20, formatColor(0.7, 0.3, 0.0), endpoints=[15, -15])
    sleep(2)
