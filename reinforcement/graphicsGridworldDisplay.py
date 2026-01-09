"""
Graphics display for Gridworld environments.

This module provides visualization capabilities for Gridworld environments using tkinter graphics.
It handles the graphical display of:
- Grid layout with obstacles and terminal states
- State values and optimal policies
- Q-values for state-action pairs
- Current agent location and movement
- Value iteration and Q-learning results

The display is highly configurable with options for:
- Window and grid size
- Animation speed
- Colors and fonts
- Display modes (values/policy/Q-values)
- Custom messages and labels

The graphics use tkinter for cross-platform compatibility and smooth animation.
All drawing is done on a tkinter Canvas with configurable visual parameters.

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added type hints throughout module
- Added detailed display configuration options
- Added Python version compatibility note
- Added last modified date and modifier
- Verified Python 3.13 compatibility

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
"""

import util
from graphicsUtils import *
from functools import reduce
from typing import Dict, List, Tuple, Optional, Any, Union

class GraphicsGridworldDisplay:
    """Handles the graphical display of a Gridworld environment."""

    def __init__(self, gridworld: Any, size: int = 120, speed: float = 1.0) -> None:
        """
        Initialize the display.
        
        Args:
            gridworld: The gridworld environment to display
            size: Size of the display in pixels
            speed: Animation speed multiplier
        """
        self.gridworld = gridworld
        self.size = size
        self.speed = speed

    def start(self) -> None:
        """Initialize and show the graphics window."""
        setup(self.gridworld, size=self.size)

    def pause(self) -> None:
        """Pause and wait for user input."""
        wait_for_keys()

    def displayValues(self, agent: Any, currentState: Optional[Tuple[int, int]] = None, message: str = 'Agent Values') -> None:
        """
        Display the values and policy for each state.
        
        Args:
            agent: Agent containing value/policy functions
            currentState: Current state to highlight
            message: Message to display below grid
        """
        values = util.Counter()
        policy = {}
        states = self.gridworld.getStates()
        for state in states:
            values[state] = agent.getValue(state)
            policy[state] = agent.getPolicy(state)
        drawValues(self.gridworld, values, policy, currentState, message)
        sleep(0.05 / self.speed)

    def displayNullValues(self, currentState: Optional[Tuple[int, int]] = None, message: str = '') -> None:
        """
        Display grid with no values.
        
        Args:
            currentState: Current state to highlight
            message: Message to display below grid
        """
        values = util.Counter()
        #policy = {}
        states = self.gridworld.getStates()
        for state in states:
            values[state] = 0.0
            #policy[state] = agent.getPolicy(state)
        drawNullValues(self.gridworld, currentState,'')
        # drawValues(self.gridworld, values, policy, currentState, message)
        sleep(0.05 / self.speed)

    def displayQValues(self, agent: Any, currentState: Optional[Tuple[int, int]] = None, message: str = 'Agent Q-Values') -> None:
        """
        Display Q-values for each state-action pair.
        
        Args:
            agent: Agent containing Q-value function
            currentState: Current state to highlight  
            message: Message to display below grid
        """
        qValues = util.Counter()
        states = self.gridworld.getStates()
        for state in states:
            for action in self.gridworld.getPossibleActions(state):
                qValues[(state, action)] = agent.getQValue(state, action)
        drawQValues(self.gridworld, qValues, currentState, message)
        sleep(0.05 / self.speed)

BACKGROUND_COLOR = formatColor(0,0,0)
EDGE_COLOR = formatColor(1,1,1)
OBSTACLE_COLOR = formatColor(0.5,0.5,0.5)
TEXT_COLOR = formatColor(1,1,1)
MUTED_TEXT_COLOR = formatColor(0.7,0.7,0.7)
LOCATION_COLOR = formatColor(0,0,1)

WINDOW_SIZE = -1
GRID_SIZE = -1
GRID_HEIGHT = -1
MARGIN = -1

def setup(gridworld: Any, title: str = "Gridworld Display", size: int = 120) -> None:
    """
    Initialize the graphics window and grid.
    
    Args:
        gridworld: The gridworld environment to display
        title: Window title
        size: Display size in pixels
    """
    global GRID_SIZE, MARGIN, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_HEIGHT
    grid = gridworld.grid
    WINDOW_SIZE = size
    GRID_SIZE = size
    GRID_HEIGHT = grid.height
    MARGIN = GRID_SIZE * 0.75
    screen_width = (grid.width - 1) * GRID_SIZE + MARGIN * 2
    screen_height = (grid.height - 0.5) * GRID_SIZE + MARGIN * 2

    begin_graphics(screen_width,
                   screen_height,
                   BACKGROUND_COLOR, title=title)

def drawNullValues(gridworld: Any, currentState: Optional[Tuple[int, int]] = None, message: str = '') -> None:
    """
    Draw grid with no values.
    
    Args:
        gridworld: The gridworld environment
        currentState: Current state to highlight
        message: Message to display below grid
    """
    grid = gridworld.grid
    blank()
    for x in range(grid.width):
        for y in range(grid.height):
            state = (x, y)
            gridType = grid[x][y]
            isExit = (str(gridType) != gridType)
            isCurrent = (currentState == state)
            if gridType == '#':
                drawSquare(x, y, 0, 0, 0, None, None, True, False, isCurrent)
            else:
                drawNullSquare(gridworld.grid, x, y, False, isExit, isCurrent)
    pos = to_screen(((grid.width - 1.0) / 2.0, - 0.8))
    text( pos, TEXT_COLOR, message, "Courier", -32, "bold", "c")


def drawValues(gridworld: Any, values: Dict, policy: Dict, currentState: Optional[Tuple[int, int]] = None, message: str = 'State Values') -> None:
    """
    Draw grid with state values and policy.
    
    Args:
        gridworld: The gridworld environment
        values: Dictionary mapping states to values
        policy: Dictionary mapping states to actions
        currentState: Current state to highlight
        message: Message to display below grid
    """
    grid = gridworld.grid
    blank()
    valueList = [values[state] for state in gridworld.getStates()] + [0.0]
    minValue = min(valueList)
    maxValue = max(valueList)
    for x in range(grid.width):
        for y in range(grid.height):
            state = (x, y)
            gridType = grid[x][y]
            isExit = (str(gridType) != gridType)
            isCurrent = (currentState == state)
            if gridType == '#':
                drawSquare(x, y, 0, 0, 0, None, None, True, False, isCurrent)
            else:
                value = values[state]
                action = None
                if policy != None and state in policy:
                    action = policy[state]
                    actions = gridworld.getPossibleActions(state)
                if action not in actions and 'exit' in actions:
                    action = 'exit'
                valString = f'{value:.2f}'
                drawSquare(x, y, value, minValue, maxValue, valString, action, False, isExit, isCurrent)
    pos = to_screen(((grid.width - 1.0) / 2.0, - 0.8))
    text( pos, TEXT_COLOR, message, "Courier", -32, "bold", "c")

def drawQValues(gridworld: Any, qValues: Dict, currentState: Optional[Tuple[int, int]] = None, message: str = 'State-Action Q-Values') -> None:
    """
    Draw grid with Q-values for state-action pairs.
    
    Args:
        gridworld: The gridworld environment
        qValues: Dictionary mapping (state,action) pairs to Q-values
        currentState: Current state to highlight
        message: Message to display below grid
    """
    grid = gridworld.grid
    blank()
    stateCrossActions = [[(state, action) for action in gridworld.getPossibleActions(state)] for state in gridworld.getStates()]
    qStates = reduce(lambda x,y: x+y, stateCrossActions, [])
    qValueList = [qValues[(state, action)] for state, action in qStates] + [0.0]
    minValue = min(qValueList)
    maxValue = max(qValueList)
    for x in range(grid.width):
        for y in range(grid.height):
            state = (x, y)
            gridType = grid[x][y]
            isExit = (str(gridType) != gridType)
            isCurrent = (currentState == state)
            actions = gridworld.getPossibleActions(state)
            if actions == None or len(actions) == 0:
                actions = [None]
            bestQ = max([qValues[(state, action)] for action in actions])
            bestActions = [action for action in actions if qValues[(state, action)] == bestQ]

            q = util.Counter()
            valStrings = {}
            for action in actions:
                v = qValues[(state, action)]
                q[action] += v
                valStrings[action] = f'{v:.2f}'
            if gridType == '#':
                drawSquare(x, y, 0, 0, 0, None, None, True, False, isCurrent)
            elif isExit:
                action = 'exit'
                value = q[action]
                valString = f'{value:.2f}'
                drawSquare(x, y, value, minValue, maxValue, valString, action, False, isExit, isCurrent)
            else:
                drawSquareQ(x, y, q, minValue, maxValue, valStrings, actions, isCurrent)
    pos = to_screen(((grid.width - 1.0) / 2.0, - 0.8))
    text( pos, TEXT_COLOR, message, "Courier", -32, "bold", "c")


def blank() -> None:
    """Clear the display."""
    clear_screen()

def drawNullSquare(grid: Any, x: int, y: int, isObstacle: bool, isTerminal: bool, isCurrent: bool) -> None:
    """
    Draw a square cell with no value.
    
    Args:
        grid: The grid environment
        x,y: Grid coordinates
        isObstacle: Whether cell is an obstacle
        isTerminal: Whether cell is terminal state
        isCurrent: Whether cell is current state
    """
    square_color = getColor(0, -1, 1)

    if isObstacle:
        square_color = OBSTACLE_COLOR

    (screen_x, screen_y) = to_screen((x, y))
    square( (screen_x, screen_y),
                   0.5* GRID_SIZE,
                   color = square_color,
                   filled = 1,
                   width = 1)

    square( (screen_x, screen_y),
                   0.5* GRID_SIZE,
                   color = EDGE_COLOR,
                   filled = 0,
                   width = 3)

    if isTerminal and not isObstacle:
        square( (screen_x, screen_y),
                     0.4* GRID_SIZE,
                     color = EDGE_COLOR,
                     filled = 0,
                     width = 2)
        text( (screen_x, screen_y),
               TEXT_COLOR,
               str(grid[x][y]),
               "Courier", -24, "bold", "c")


    text_color = TEXT_COLOR

    if not isObstacle and isCurrent:
        circle( (screen_x, screen_y), 0.1*GRID_SIZE, LOCATION_COLOR, fillColor=LOCATION_COLOR )

    # if not isObstacle:
    #   text( (screen_x, screen_y), text_color, valStr, "Courier", 24, "bold", "c")

def drawSquare(x: int, y: int, val: float, min: float, max: float, valStr: Optional[str], action: Optional[str], 
               isObstacle: bool, isTerminal: bool, isCurrent: bool) -> None:
    """
    Draw a square cell with value and action.
    
    Args:
        x,y: Grid coordinates
        val: Value to display
        min,max: Value range for color scaling
        valStr: Value string to display
        action: Action to display
        isObstacle: Whether cell is obstacle
        isTerminal: Whether cell is terminal
        isCurrent: Whether cell is current state
    """
    square_color = getColor(val, min, max)

    if isObstacle:
        square_color = OBSTACLE_COLOR

    (screen_x, screen_y) = to_screen((x, y))
    square( (screen_x, screen_y),
                   0.5* GRID_SIZE,
                   color = square_color,
                   filled = 1,
                   width = 1)
    square( (screen_x, screen_y),
                   0.5* GRID_SIZE,
                   color = EDGE_COLOR,
                   filled = 0,
                   width = 3)
    if isTerminal and not isObstacle:
        square( (screen_x, screen_y),
                     0.4* GRID_SIZE,
                     color = EDGE_COLOR,
                     filled = 0,
                     width = 2)


    if action == 'north':
        polygon( [(screen_x, screen_y - 0.45*GRID_SIZE), (screen_x+0.05*GRID_SIZE, screen_y-0.40*GRID_SIZE), (screen_x-0.05*GRID_SIZE, screen_y-0.40*GRID_SIZE)], EDGE_COLOR, filled = 1, smoothed = False)
    if action == 'south':
        polygon( [(screen_x, screen_y + 0.45*GRID_SIZE), (screen_x+0.05*GRID_SIZE, screen_y+0.40*GRID_SIZE), (screen_x-0.05*GRID_SIZE, screen_y+0.40*GRID_SIZE)], EDGE_COLOR, filled = 1, smoothed = False)
    if action == 'west':
        polygon( [(screen_x-0.45*GRID_SIZE, screen_y), (screen_x-0.4*GRID_SIZE, screen_y+0.05*GRID_SIZE), (screen_x-0.4*GRID_SIZE, screen_y-0.05*GRID_SIZE)], EDGE_COLOR, filled = 1, smoothed = False)
    if action == 'east':
        polygon( [(screen_x+0.45*GRID_SIZE, screen_y), (screen_x+0.4*GRID_SIZE, screen_y+0.05*GRID_SIZE), (screen_x+0.4*GRID_SIZE, screen_y-0.05*GRID_SIZE)], EDGE_COLOR, filled = 1, smoothed = False)


    text_color = TEXT_COLOR

    if not isObstacle and isCurrent:
        circle( (screen_x, screen_y), 0.1*GRID_SIZE, outlineColor=LOCATION_COLOR, fillColor=LOCATION_COLOR )

    if not isObstacle:
        text( (screen_x, screen_y), text_color, valStr, "Courier", -30, "bold", "c")


def drawSquareQ(x: int, y: int, qVals: Dict, minVal: float, maxVal: float, valStrs: Dict, bestActions: List, isCurrent: bool) -> None:
    """
    Draw a square cell with Q-values.
    
    Args:
        x,y: Grid coordinates
        qVals: Dictionary of Q-values for each action
        minVal,maxVal: Value range for color scaling
        valStrs: Dictionary of value strings for each action
        bestActions: List of actions with highest Q-value
        isCurrent: Whether cell is current state
    """
    (screen_x, screen_y) = to_screen((x, y))

    center = (screen_x, screen_y)
    nw = (screen_x-0.5*GRID_SIZE, screen_y-0.5*GRID_SIZE)
    ne = (screen_x+0.5*GRID_SIZE, screen_y-0.5*GRID_SIZE)
    se = (screen_x+0.5*GRID_SIZE, screen_y+0.5*GRID_SIZE)
    sw = (screen_x-0.5*GRID_SIZE, screen_y+0.5*GRID_SIZE)
    n = (screen_x, screen_y-0.5*GRID_SIZE+5)
    s = (screen_x, screen_y+0.5*GRID_SIZE-5)
    w = (screen_x-0.5*GRID_SIZE+5, screen_y)
    e = (screen_x+0.5*GRID_SIZE-5, screen_y)

    actions = list(qVals.keys())
    for action in actions:

        wedge_color = getColor(qVals[action], minVal, maxVal)

        if action == 'north':
            polygon( (center, nw, ne), wedge_color, filled = 1, smoothed = False)
            #text(n, text_color, valStr, "Courier", 8, "bold", "n")
        if action == 'south':
            polygon( (center, sw, se), wedge_color, filled = 1, smoothed = False)
            #text(s, text_color, valStr, "Courier", 8, "bold", "s")
        if action == 'east':
            polygon( (center, ne, se), wedge_color, filled = 1, smoothed = False)
            #text(e, text_color, valStr, "Courier", 8, "bold", "e")
        if action == 'west':
            polygon( (center, nw, sw), wedge_color, filled = 1, smoothed = False)
            #text(w, text_color, valStr, "Courier", 8, "bold", "w")

    square( (screen_x, screen_y),
                   0.5* GRID_SIZE,
                   color = EDGE_COLOR,
                   filled = 0,
                   width = 3)
    line(ne, sw, color = EDGE_COLOR)
    line(nw, se, color = EDGE_COLOR)

    if isCurrent:
        circle( (screen_x, screen_y), 0.1*GRID_SIZE, LOCATION_COLOR, fillColor=LOCATION_COLOR )

    for action in actions:
        text_color = TEXT_COLOR
        if qVals[action] < max(qVals.values()): text_color = MUTED_TEXT_COLOR
        valStr = ""
        if action in valStrs:
            valStr = valStrs[action]
        h = -20
        if action == 'north':
            #polygon( (center, nw, ne), wedge_color, filled = 1, smooth = 0)
            text(n, text_color, valStr, "Courier", h, "bold", "n")
        if action == 'south':
            #polygon( (center, sw, se), wedge_color, filled = 1, smooth = 0)
            text(s, text_color, valStr, "Courier", h, "bold", "s")
        if action == 'east':
            #polygon( (center, ne, se), wedge_color, filled = 1, smooth = 0)
            text(e, text_color, valStr, "Courier", h, "bold", "e")
        if action == 'west':
            #polygon( (center, nw, sw), wedge_color, filled = 1, smooth = 0)
            text(w, text_color, valStr, "Courier", h, "bold", "w")


def getColor(val: float, minVal: float, max: float) -> str:
    """
    Get color for value based on range.
    
    Args:
        val: Value to get color for
        minVal: Minimum value in range
        max: Maximum value in range
        
    Returns:
        Hex color string
    """
    r, g = 0.0, 0.0
    if val < 0 and minVal < 0:
        r = val * 0.65 / minVal
    if val > 0 and max > 0:
        g = val * 0.65 / max
    return formatColor(r,g,0.0)


def square(pos: Tuple[float, float], size: float, color: str, filled: bool, width: int) -> Any:
    """
    Draw a square.
    
    Args:
        pos: (x,y) position
        size: Square size
        color: Color string
        filled: Whether to fill square
        width: Line width
        
    Returns:
        Polygon object
    """
    x, y = pos
    dx, dy = size, size
    return polygon([(x - dx, y - dy), (x - dx, y + dy), (x + dx, y + dy), (x + dx, y - dy)], outlineColor=color, fillColor=color, filled=filled, width=width, smoothed=False)


def to_screen(point: Tuple[float, float]) -> Tuple[float, float]:
    """
    Convert grid coordinates to screen coordinates.
    
    Args:
        point: (x,y) grid position
        
    Returns:
        (x,y) screen position
    """
    ( gamex, gamey ) = point
    x = gamex*GRID_SIZE + MARGIN
    y = (GRID_HEIGHT - gamey - 1)*GRID_SIZE + MARGIN
    return ( x, y )

def to_grid(point: Tuple[float, float]) -> Tuple[int, int]:
    """
    Convert screen coordinates to grid coordinates.
    
    Args:
        point: (x,y) screen position
        
    Returns:
        (x,y) grid position
    """
    (x, y) = point
    x = int ((y - MARGIN + GRID_SIZE * 0.5) / GRID_SIZE)
    y = int ((x - MARGIN + GRID_SIZE * 0.5) / GRID_SIZE)
    print(f"{point} --> {(x, y)}")
    return (x, y)
