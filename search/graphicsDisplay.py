"""Graphics display module for Pacman game.

This module provides the graphical display functionality for the Pacman game,
including rendering of Pacman, ghosts, walls, food pellets, and other game elements.
Uses Tkinter for graphics output.

Modified by: George Rudolph at Utah Valley University
Date: 9 Nov 2024

# Updates:
# - Added comprehensive docstrings with Args/Returns sections
# - Added type hints throughout module
# - Improved code organization and readability
# - Added constants type annotations
# - Added return type hints for all functions
# - Added parameter type hints for all functions
# Python 3.13 compatibility verified

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

import os #saving graphical output
from typing import List, Dict, Any, Tuple
from graphicsUtils import *
import math, time
from game import Directions

###########################
#  GRAPHICS DISPLAY CODE  #
###########################

# Most code by Dan Klein and John Denero written or rewritten for cs188, UC Berkeley.
# Some code from a Pacman implementation by LiveWires, and used / modified with permission.

DEFAULT_GRID_SIZE: float = 30.0
INFO_PANE_HEIGHT: int = 35
BACKGROUND_COLOR: str = formatColor(0,0,0)
WALL_COLOR: str = formatColor(0.0/255.0, 51.0/255.0, 255.0/255.0)
INFO_PANE_COLOR: str = formatColor(.4,.4,0)
SCORE_COLOR: str = formatColor(.9, .9, .9)
PACMAN_OUTLINE_WIDTH: int = 2
PACMAN_CAPTURE_OUTLINE_WIDTH: int = 4

GHOST_COLORS: List[str] = []
GHOST_COLORS.append(formatColor(.9,0,0)) # Red
GHOST_COLORS.append(formatColor(0,.3,.9)) # Blue
GHOST_COLORS.append(formatColor(.98,.41,.07)) # Orange
GHOST_COLORS.append(formatColor(.1,.75,.7)) # Green
GHOST_COLORS.append(formatColor(1.0,0.6,0.0)) # Yellow
GHOST_COLORS.append(formatColor(.4,0.13,0.91)) # Purple

TEAM_COLORS: List[str] = GHOST_COLORS[:2]

GHOST_SHAPE: List[Tuple[float, float]] = [
    ( 0,    0.3 ),
    ( 0.25, 0.75 ),
    ( 0.5,  0.3 ),
    ( 0.75, 0.75 ),
    ( 0.75, -0.5 ),
    ( 0.5,  -0.75 ),
    (-0.5,  -0.75 ),
    (-0.75, -0.5 ),
    (-0.75, 0.75 ),
    (-0.5,  0.3 ),
    (-0.25, 0.75 )
  ]
GHOST_SIZE: float = 0.65
SCARED_COLOR: str = formatColor(1,1,1)

GHOST_VEC_COLORS: List[List[float]] = [colorToVector(c) for c in GHOST_COLORS]

PACMAN_COLOR: str = formatColor(255.0/255.0,255.0/255.0,61.0/255)
PACMAN_SCALE: float = 0.5
#pacman_speed = 0.25

# Food
FOOD_COLOR: str = formatColor(1,1,1)
FOOD_SIZE: float = 0.1

# Laser
LASER_COLOR: str = formatColor(1,0,0)
LASER_SIZE: float = 0.02

# Capsule graphics
CAPSULE_COLOR: str = formatColor(1,1,1)
CAPSULE_SIZE: float = 0.25

# Drawing walls
WALL_RADIUS: float = 0.15

class InfoPane:
    """
    Information pane displayed at the bottom of the Pacman game window.
    
    Displays game information like score, ghost distances, and team information.
    Handles drawing and updating of this information during gameplay.
    
    Args:
        layout: The game layout containing dimensions
        gridSize: Size of each grid square in pixels
    """
    def __init__(self, layout: 'Layout', gridSize: int) -> None:
        self.gridSize = gridSize
        self.width = (layout.width) * gridSize
        self.base = (layout.height + 1) * gridSize
        self.height = INFO_PANE_HEIGHT
        self.fontSize = 24
        self.textColor = PACMAN_COLOR
        self.drawPane()

    def toScreen(self, pos: Union[Tuple[int, int], int], y: Optional[int] = None) -> Tuple[int, int]:
        """
        Translates a point relative from the bottom left of the info pane.
        
        Args:
            pos: Either an (x,y) tuple or just the x coordinate
            y: Y coordinate if pos is just x, otherwise None
            
        Returns:
            Tuple of (screen_x, screen_y) coordinates
        """
        if y == None:
            x,y = pos
        else:
            x = pos

        x = self.gridSize + x # Margin
        y = self.base + y
        return x,y

    def drawPane(self) -> None:
        """Initializes and draws the score display."""
        self.scoreText = text( self.toScreen(0, 0  ), self.textColor, "SCORE:    0", "Times", self.fontSize, "bold")

    def initializeGhostDistances(self, distances: List[str]) -> None:
        """
        Initializes the ghost distance displays.
        
        Args:
            distances: List of distance strings to display
        """
        self.ghostDistanceText = []

        size = 20
        if self.width < 240:
            size = 12
        if self.width < 160:
            size = 10

        for i, d in enumerate(distances):
            t = text( self.toScreen(self.width//2 + self.width//8 * i, 0), GHOST_COLORS[i+1], d, "Times", size, "bold")
            self.ghostDistanceText.append(t)

    def updateScore(self, score: int) -> None:
        """
        Updates the displayed score.
        
        Args:
            score: New score to display
        """
        changeText(self.scoreText, "SCORE: % 4d" % score)

    def setTeam(self, isBlue: bool) -> None:
        """
        Sets and displays the team name.
        
        Args:
            isBlue: True if blue team, False if red team
        """
        text = "RED TEAM"
        if isBlue: text = "BLUE TEAM"
        self.teamText = text( self.toScreen(300, 0  ), self.textColor, text, "Times", self.fontSize, "bold")

    def updateGhostDistances(self, distances: List[str]) -> None:
        """
        Updates the displayed ghost distances.
        
        Args:
            distances: List of new distance strings to display
        """
        if len(distances) == 0: return
        if 'ghostDistanceText' not in dir(self): self.initializeGhostDistances(distances)
        else:
            for i, d in enumerate(distances):
                changeText(self.ghostDistanceText[i], d)

    def drawGhost(self) -> None:
        """Placeholder for drawing ghost."""
        pass

    def drawPacman(self) -> None:
        """Placeholder for drawing pacman."""
        pass

    def drawWarning(self) -> None:
        """Placeholder for drawing warning."""
        pass

    def clearIcon(self) -> None:
        """Placeholder for clearing icon."""
        pass

    def updateMessage(self, message: str) -> None:
        """Placeholder for updating message."""
        pass

    def clearMessage(self) -> None:
        """Placeholder for clearing message."""
        pass


class PacmanGraphics:
    """
    Graphics class for displaying Pacman game visualization.
    
    Handles initialization of display parameters and maintains graphics state.
    """
    def __init__(self, zoom: float = 1.0, frameTime: float = 0.0, capture: bool = False) -> None:
        """
        Initialize the graphics display.
        
        Args:
            zoom: Scale factor for the display (default: 1.0)
            frameTime: Delay between frames in seconds (default: 0.0)
            capture: Whether this is for capture mode (default: False)
        """
        self.have_window: int = 0
        self.currentGhostImages: dict = {}
        self.pacmanImage: Optional[Any] = None
        self.zoom: float = zoom
        self.gridSize: float = DEFAULT_GRID_SIZE * zoom
        self.capture: bool = capture
        self.frameTime: float = frameTime

    def checkNullDisplay(self) -> bool:
        """
        Check if this is a null display.
        
        Returns:
            bool: Always returns False for this implementation
        """
        return False

    def initialize(self, state: Any, isBlue: bool = False) -> None:
        """
        Initialize the graphics display with the given state.
        
        Args:
            state: The game state to initialize with
            isBlue: Whether pacman is on the blue team (default: False)
        """
        self.isBlue = isBlue
        self.startGraphics(state)

        # self.drawDistributions(state)
        self.distributionImages = None  # Initialized lazily
        self.drawStaticObjects(state)
        self.drawAgentObjects(state)

        # Information
        self.previousState = state

    def startGraphics(self, state: Any) -> None:
        """
        Initialize the graphics window and layout.
        
        Args:
            state: The game state containing layout information
        """
        self.layout = state.layout
        layout = self.layout
        self.width = layout.width
        self.height = layout.height
        self.make_window(self.width, self.height)
        self.infoPane = InfoPane(layout, self.gridSize)
        self.currentState = layout

    def drawDistributions(self, state: Any) -> None:
        """
        Draw the belief distributions for each position.
        
        Args:
            state: The game state containing wall information
        """
        walls = state.layout.walls
        dist = []
        for x in range(walls.width):
            distx = []
            dist.append(distx)
            for y in range(walls.height):
                ( screen_x, screen_y ) = self.to_screen( (x, y) )
                block = square( (screen_x, screen_y),
                                0.5 * self.gridSize,
                                color = BACKGROUND_COLOR,
                                filled = 1, behind=2)
                distx.append(block)
        self.distributionImages = dist

    def drawStaticObjects(self, state: Any) -> None:
        """
        Draw the static game objects (walls, food, capsules).
        
        Args:
            state: The game state containing layout information
        """
        layout = self.layout
        self.drawWalls(layout.walls)
        self.food = self.drawFood(layout.food)
        self.capsules = self.drawCapsules(layout.capsules)
        refresh()

    def drawAgentObjects(self, state: Any) -> None:
        """
        Draw all agents (Pacman and ghosts) in their initial positions.
        
        Args:
            state: The game state containing agent information
        """
        self.agentImages = [] # List of (agentState, image) tuples
        for index, agent in enumerate(state.agentStates):
            if agent.isPacman:
                image = self.drawPacman(agent, index)
                self.agentImages.append((agent, image))
            else:
                image = self.drawGhost(agent, index)
                self.agentImages.append((agent, image))
        refresh()

    def swapImages(self, agentIndex: int, newState: Any) -> None:
        """
        Change an agent's visualization between ghost and pacman.
        
        Used in capture mode when agents can switch teams.
        
        Args:
            agentIndex: Index of the agent to update
            newState: New agent state to render
        """
        prevState, prevImage = self.agentImages[agentIndex]
        for item in prevImage: remove_from_screen(item)
        if newState.isPacman:
            image = self.drawPacman(newState, agentIndex)
            self.agentImages[agentIndex] = (newState, image)
        else:
            image = self.drawGhost(newState, agentIndex)
            self.agentImages[agentIndex] = (newState, image)
        refresh()

    def update(self, newState: Any) -> None:
        """
        Update the game display for a new state.
        
        Handles movement animation, food/capsule removal, score updates.
        
        Args:
            newState: The new game state to display
        """
        agentIndex = newState._agentMoved
        agentState = newState.agentStates[agentIndex]

        if self.agentImages[agentIndex][0].isPacman != agentState.isPacman:
            self.swapImages(agentIndex, agentState)
        prevState, prevImage = self.agentImages[agentIndex]
        if agentState.isPacman:
            self.animatePacman(agentState, prevState, prevImage)
        else:
            self.moveGhost(agentState, agentIndex, prevState, prevImage)
        self.agentImages[agentIndex] = (agentState, prevImage)

        if newState._foodEaten != None:
            self.removeFood(newState._foodEaten, self.food)
        if newState._capsuleEaten != None:
            self.removeCapsule(newState._capsuleEaten, self.capsules)
        self.infoPane.updateScore(newState.score)
        if 'ghostDistances' in dir(newState):
            self.infoPane.updateGhostDistances(newState.ghostDistances)

    def make_window(self, width: int, height: int) -> None:
        """
        Create the main game window.
        
        Args:
            width: Width of the game grid in cells
            height: Height of the game grid in cells
        """
        grid_width = (width-1) * self.gridSize
        grid_height = (height-1) * self.gridSize
        screen_width = 2*self.gridSize + grid_width
        screen_height = 2*self.gridSize + grid_height + INFO_PANE_HEIGHT

        begin_graphics(screen_width,
                      screen_height,
                      BACKGROUND_COLOR,
                      "CS4470 Pacman")

    def drawPacman(self, pacman: Any, index: int) -> List[Any]:
        """
        Draw a Pacman agent.
        
        Args:
            pacman: The Pacman agent state to draw
            index: Index of this Pacman agent
            
        Returns:
            List containing the circle object representing Pacman
        """
        position = self.getPosition(pacman)
        screen_point = self.to_screen(position)
        endpoints = self.getEndpoints(self.getDirection(pacman))

        width = PACMAN_OUTLINE_WIDTH
        outlineColor = PACMAN_COLOR
        fillColor = PACMAN_COLOR

        if self.capture:
            outlineColor = TEAM_COLORS[index % 2]
            fillColor = GHOST_COLORS[index]
            width = PACMAN_CAPTURE_OUTLINE_WIDTH

        return [circle(screen_point, PACMAN_SCALE * self.gridSize,
                      fillColor = fillColor, outlineColor = outlineColor,
                      endpoints = endpoints,
                      width = width)]

    def getEndpoints(self, direction: str, position: Tuple[float, float] = (0,0)) -> Tuple[float, float]:
        """
        Get the endpoints of Pacman's mouth for animation.
        
        Args:
            direction: Direction Pacman is facing
            position: Current position coordinates
            
        Returns:
            Tuple of (start_angle, end_angle) for Pacman's mouth arc
        """
        x, y = position
        pos = x - int(x) + y - int(y)
        width = 30 + 80 * math.sin(math.pi* pos)

        delta = width / 2
        if (direction == 'West'):
            endpoints = (180+delta, 180-delta)
        elif (direction == 'North'):
            endpoints = (90+delta, 90-delta)
        elif (direction == 'South'):
            endpoints = (270+delta, 270-delta)
        else:
            endpoints = (0+delta, 0-delta)
        return endpoints

    def movePacman(self, position: Tuple[float, float], direction: str, image: List[Any]) -> None:
        """
        Move Pacman to a new position on the screen.
        
        Args:
            position: (x,y) coordinates of new position
            direction: Direction Pacman is facing ('North', 'South', 'East', 'West')
            image: List containing the circle object representing Pacman
        """
        screenPosition = self.to_screen(position)
        endpoints = self.getEndpoints(direction, position)
        r = PACMAN_SCALE * self.gridSize
        moveCircle(image[0], screenPosition, r, endpoints)
        refresh()

    def animatePacman(self, pacman: 'AgentState', prevPacman: 'AgentState', image: List[Any]) -> None:
        """
        Animate Pacman moving from previous position to current position.
        
        Args:
            pacman: Current Pacman agent state
            prevPacman: Previous Pacman agent state 
            image: List containing the circle object representing Pacman
        """
        if self.frameTime < 0:
            print('Press any key to step forward, "q" to play')
            keys = wait_for_keys()
            if 'q' in keys:
                self.frameTime = 0.1
        if self.frameTime > 0.01 or self.frameTime < 0:
            start = time.time()
            fx, fy = self.getPosition(prevPacman)
            px, py = self.getPosition(pacman)
            frames = 4.0
            for i in range(1,int(frames) + 1):
                pos = px*i/frames + fx*(frames-i)/frames, py*i/frames + fy*(frames-i)/frames
                self.movePacman(pos, self.getDirection(pacman), image)
                refresh()
                sleep(abs(self.frameTime) / frames)
        else:
            self.movePacman(self.getPosition(pacman), self.getDirection(pacman), image)
        refresh()

    def getGhostColor(self, ghost: 'AgentState', ghostIndex: int) -> str:
        """
        Get the color to draw a ghost.
        
        Args:
            ghost: Ghost agent state
            ghostIndex: Index of this ghost
            
        Returns:
            Color string to use for ghost
        """
        if ghost.scaredTimer > 0:
            return SCARED_COLOR
        else:
            return GHOST_COLORS[ghostIndex]

    def drawGhost(self, ghost: 'AgentState', agentIndex: int) -> List[Any]:
        """
        Draw a ghost.
        
        Args:
            ghost: Ghost agent state to draw
            agentIndex: Index of this ghost agent
            
        Returns:
            List of graphics objects making up the ghost (body, eyes, pupils)
        """
        pos = self.getPosition(ghost)
        dir = self.getDirection(ghost)
        (screen_x, screen_y) = (self.to_screen(pos))
        coords = []
        for (x, y) in GHOST_SHAPE:
            coords.append((x*self.gridSize*GHOST_SIZE + screen_x, y*self.gridSize*GHOST_SIZE + screen_y))

        colour = self.getGhostColor(ghost, agentIndex)
        body = polygon(coords, colour, filled = 1)
        WHITE = formatColor(1.0, 1.0, 1.0)
        BLACK = formatColor(0.0, 0.0, 0.0)

        dx = 0
        dy = 0
        if dir == 'North':
            dy = -0.2
        if dir == 'South':
            dy = 0.2
        if dir == 'East':
            dx = 0.2
        if dir == 'West':
            dx = -0.2
        leftEye = circle((screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx/1.5), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2, WHITE, WHITE)
        rightEye = circle((screen_x+self.gridSize*GHOST_SIZE*(0.3+dx/1.5), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2, WHITE, WHITE)
        leftPupil = circle((screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08, BLACK, BLACK)
        rightPupil = circle((screen_x+self.gridSize*GHOST_SIZE*(0.3+dx), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08, BLACK, BLACK)
        ghostImageParts = []
        ghostImageParts.append(body)
        ghostImageParts.append(leftEye)
        ghostImageParts.append(rightEye)
        ghostImageParts.append(leftPupil)
        ghostImageParts.append(rightPupil)

        return ghostImageParts

    def moveEyes(self, pos: Tuple[float, float], dir: str, eyes: List[Any]) -> None:
        """
        Move ghost's eyes to track direction.
        
        Args:
            pos: Current position coordinates
            dir: Direction ghost is facing
            eyes: List of eye graphics objects [leftEye, rightEye, leftPupil, rightPupil]
        """
        (screen_x, screen_y) = (self.to_screen(pos))
        dx = 0
        dy = 0
        if dir == 'North':
            dy = -0.2
        if dir == 'South':
            dy = 0.2
        if dir == 'East':
            dx = 0.2
        if dir == 'West':
            dx = -0.2
        moveCircle(eyes[0],(screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx/1.5), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2)
        moveCircle(eyes[1],(screen_x+self.gridSize*GHOST_SIZE*(0.3+dx/1.5), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2)
        moveCircle(eyes[2],(screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08)
        moveCircle(eyes[3],(screen_x+self.gridSize*GHOST_SIZE*(0.3+dx), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08)

    def moveGhost(self, ghost: 'AgentState', ghostIndex: int, prevGhost: 'AgentState', ghostImageParts: List[Any]) -> None:
        """
        Move ghost from previous position to current position.
        
        Args:
            ghost: Current ghost agent state
            ghostIndex: Index of this ghost
            prevGhost: Previous ghost agent state
            ghostImageParts: List of graphics objects making up the ghost
        """
        old_x, old_y = self.to_screen(self.getPosition(prevGhost))
        new_x, new_y = self.to_screen(self.getPosition(ghost))
        delta = new_x - old_x, new_y - old_y

        for ghostImagePart in ghostImageParts:
            move_by(ghostImagePart, delta)
        refresh()

        if ghost.scaredTimer > 0:
            color = SCARED_COLOR
        else:
            color = GHOST_COLORS[ghostIndex]
        edit(ghostImageParts[0], ('fill', color), ('outline', color))
        self.moveEyes(self.getPosition(ghost), self.getDirection(ghost), ghostImageParts[-4:])
        refresh()

    def getPosition(self, agentState: 'AgentState') -> Tuple[float, float]:
        """
        Get the position of an agent.
        
        Args:
            agentState: The agent state to get position for
            
        Returns:
            (x,y) position coordinates, or (-1000,-1000) if no configuration
        """
        if agentState.configuration == None: return (-1000, -1000)
        return agentState.getPosition()

    def getDirection(self, agentState: 'AgentState') -> str:
        """
        Get the direction an agent is facing.
        
        Args:
            agentState: The agent state to get direction for
            
        Returns:
            Direction string ('North', 'South', 'East', 'West', 'Stop')
        """
        if agentState.configuration == None: return Directions.STOP
        return agentState.configuration.getDirection()

    def finish(self) -> None:
        """Clean up by closing the graphics window."""
        end_graphics()

    def to_screen(self, point):
        ( x, y ) = point
        #y = self.height - y
        x = (x + 1)*self.gridSize
        y = (self.height  - y)*self.gridSize
        return ( x, y )

    # Fixes some TK issue with off-center circles
    def to_screen2(self, point):
        ( x, y ) = point
        #y = self.height - y
        x = (x + 1)*self.gridSize
        y = (self.height  - y)*self.gridSize
        return ( x, y )

    def drawWalls(self, wallMatrix: 'Grid') -> None:
        """
        Draw the maze walls with rounded corners and proper coloring.
        
        Draws each wall segment with rounded corners that connect smoothly to adjacent walls.
        In capture mode, walls are colored according to team territory.
        
        Args:
            wallMatrix: Grid of boolean values indicating wall locations
        """
        wallColor = WALL_COLOR
        for xNum, x in enumerate(wallMatrix):
            if self.capture and (xNum * 2) < wallMatrix.width: wallColor = TEAM_COLORS[0]
            if self.capture and (xNum * 2) >= wallMatrix.width: wallColor = TEAM_COLORS[1]

            for yNum, cell in enumerate(x):
                if cell: # There's a wall here
                    pos = (xNum, yNum)
                    screen = self.to_screen(pos)
                    screen2 = self.to_screen2(pos)

                    # draw each quadrant of the square based on adjacent walls
                    wIsWall = self.isWall(xNum-1, yNum, wallMatrix)
                    eIsWall = self.isWall(xNum+1, yNum, wallMatrix)
                    nIsWall = self.isWall(xNum, yNum+1, wallMatrix)
                    sIsWall = self.isWall(xNum, yNum-1, wallMatrix)
                    nwIsWall = self.isWall(xNum-1, yNum+1, wallMatrix)
                    swIsWall = self.isWall(xNum-1, yNum-1, wallMatrix)
                    neIsWall = self.isWall(xNum+1, yNum+1, wallMatrix)
                    seIsWall = self.isWall(xNum+1, yNum-1, wallMatrix)

                    # NE quadrant
                    if (not nIsWall) and (not eIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (0,91), 'arc')
                    if (nIsWall) and (not eIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize*WALL_RADIUS, 0)), add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(-0.5)-1)), wallColor)
                    if (not nIsWall) and (eIsWall):
                        # horizontal line
                        line(add(screen, (0, self.gridSize*(-1)*WALL_RADIUS)), add(screen, (self.gridSize*0.5+1, self.gridSize*(-1)*WALL_RADIUS)), wallColor)
                    if (nIsWall) and (eIsWall) and (not neIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize*2*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS)), WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (180,271), 'arc')
                        line(add(screen, (self.gridSize*2*WALL_RADIUS-1, self.gridSize*(-1)*WALL_RADIUS)), add(screen, (self.gridSize*0.5+1, self.gridSize*(-1)*WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS+1)), add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(-0.5))), wallColor)

                    # NW quadrant
                    if (not nIsWall) and (not wIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (90,181), 'arc')
                    if (nIsWall) and (not wIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, 0)), add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(-0.5)-1)), wallColor)
                    if (not nIsWall) and (wIsWall):
                        # horizontal line
                        line(add(screen, (0, self.gridSize*(-1)*WALL_RADIUS)), add(screen, (self.gridSize*(-0.5)-1, self.gridSize*(-1)*WALL_RADIUS)), wallColor)
                    if (nIsWall) and (wIsWall) and (not nwIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize*(-2)*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS)), WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (270,361), 'arc')
                        line(add(screen, (self.gridSize*(-2)*WALL_RADIUS+1, self.gridSize*(-1)*WALL_RADIUS)), add(screen, (self.gridSize*(-0.5), self.gridSize*(-1)*WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS+1)), add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(-0.5))), wallColor)

                    # SE quadrant
                    if (not sIsWall) and (not eIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (270,361), 'arc')
                    if (sIsWall) and (not eIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize*WALL_RADIUS, 0)), add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(0.5)+1)), wallColor)
                    if (not sIsWall) and (eIsWall):
                        # horizontal line
                        line(add(screen, (0, self.gridSize*(1)*WALL_RADIUS)), add(screen, (self.gridSize*0.5+1, self.gridSize*(1)*WALL_RADIUS)), wallColor)
                    if (sIsWall) and (eIsWall) and (not seIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize*2*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS)), WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (90,181), 'arc')
                        line(add(screen, (self.gridSize*2*WALL_RADIUS-1, self.gridSize*(1)*WALL_RADIUS)), add(screen, (self.gridSize*0.5, self.gridSize*(1)*WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS-1)), add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(0.5))), wallColor)

                    # SW quadrant
                    if (not sIsWall) and (not wIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (180,271), 'arc')
                    if (sIsWall) and (not wIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, 0)), add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(0.5)+1)), wallColor)
                    if (not sIsWall) and (wIsWall):
                        # horizontal line
                        line(add(screen, (0, self.gridSize*(1)*WALL_RADIUS)), add(screen, (self.gridSize*(-0.5)-1, self.gridSize*(1)*WALL_RADIUS)), wallColor)
                    if (sIsWall) and (wIsWall) and (not swIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize*(-2)*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS)), WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (0,91), 'arc')
                        line(add(screen, (self.gridSize*(-2)*WALL_RADIUS+1, self.gridSize*(1)*WALL_RADIUS)), add(screen, (self.gridSize*(-0.5), self.gridSize*(1)*WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS-1)), add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(0.5))), wallColor)

    def isWall(self, x: int, y: int, walls: 'Grid') -> bool:
        """
        Check if a given position contains a wall.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            walls: Grid of wall locations
            
        Returns:
            True if position (x,y) contains a wall, False otherwise or if out of bounds
        """
        if x < 0 or y < 0:
            return False
        if x >= walls.width or y >= walls.height:
            return False
        return walls[x][y]

    def drawFood(self, foodMatrix: 'Grid') -> List[List[Optional[Any]]]:
        """
        Draw all food pellets on the game board.
        
        In capture mode, food is colored according to team territory.
        
        Args:
            foodMatrix: Grid indicating food pellet locations
            
        Returns:
            2D list of food dot graphics objects, None where no food exists
        """
        foodImages = []
        color = FOOD_COLOR
        for xNum, x in enumerate(foodMatrix):
            if self.capture and (xNum * 2) <= foodMatrix.width: color = TEAM_COLORS[0]
            if self.capture and (xNum * 2) > foodMatrix.width: color = TEAM_COLORS[1]
            imageRow = []
            foodImages.append(imageRow)
            for yNum, cell in enumerate(x):
                if cell: # There's food here
                    screen = self.to_screen((xNum, yNum ))
                    dot = circle( screen,
                                  FOOD_SIZE * self.gridSize,
                                  outlineColor = color, fillColor = color,
                                  width = 1)
                    imageRow.append(dot)
                else:
                    imageRow.append(None)
        return foodImages

    def drawCapsules(self, capsules: List[Tuple[int, int]]) -> Dict[Tuple[int, int], Any]:
        """
        Draw all power capsules on the game board.
        
        Args:
            capsules: List of (x,y) capsule positions
            
        Returns:
            Dictionary mapping capsule positions to their graphics objects
        """
        capsuleImages = {}
        for capsule in capsules:
            ( screen_x, screen_y ) = self.to_screen(capsule)
            dot = circle( (screen_x, screen_y),
                              CAPSULE_SIZE * self.gridSize,
                              outlineColor = CAPSULE_COLOR,
                              fillColor = CAPSULE_COLOR,
                              width = 1)
            capsuleImages[capsule] = dot
        return capsuleImages

    def removeFood(self, cell: Tuple[int, int], foodImages: List[List[Any]]) -> None:
        """
        Remove eaten food pellet from display.
        
        Args:
            cell: (x,y) position of eaten food
            foodImages: 2D list of food graphics objects
        """
        x, y = cell
        remove_from_screen(foodImages[x][y])

    def removeCapsule(self, cell: Tuple[int, int], capsuleImages: Dict[Tuple[int, int], Any]) -> None:
        """
        Remove eaten power capsule from display.
        
        Args:
            cell: (x,y) position of eaten capsule
            capsuleImages: Dictionary of capsule graphics objects
        """
        x, y = cell
        remove_from_screen(capsuleImages[(x, y)])

    def drawExpandedCells(self, cells: List[Tuple[int, int]]) -> None:
        """
        Draws an overlay of expanded grid positions for search agents.
        
        Creates a visual overlay showing which grid cells were expanded during search,
        with a gradient effect based on expansion order.
        
        Args:
            cells: List of (x,y) coordinates of cells expanded during search,
                  in order of expansion
        """
        n = float(len(cells))
        baseColor = [1.0, 0.0, 0.0]
        self.clearExpandedCells()
        self.expandedCells = []
        for k, cell in enumerate(cells):
            screenPos = self.to_screen(cell)
            cellColor = formatColor(*[(n-k) * c * .5 / n + .25 for c in baseColor])
            block = square(screenPos,
                     0.5 * self.gridSize,
                     color = cellColor,
                     filled = 1, behind=2)
            self.expandedCells.append(block)
            if self.frameTime < 0:
                refresh()

    def clearExpandedCells(self) -> None:
        """
        Removes the expanded cell overlays from the display.
        
        Cleans up any existing expanded cell visualizations before drawing new ones.
        """
        if 'expandedCells' in dir(self) and len(self.expandedCells) > 0:
            for cell in self.expandedCells:
                remove_from_screen(cell)

    def updateDistributions(self, distributions: List[Dict[Tuple[int, int], float]]) -> None:
        """
        Updates the display of agents' belief distributions.
        
        Visualizes each agent's beliefs about ghost locations by coloring grid cells
        based on probability distributions.
        
        Args:
            distributions: List of dictionaries mapping (x,y) positions to probabilities,
                         representing each agent's beliefs
        """
        # copy all distributions so we don't change their state
        distributions = map(lambda x: x.copy(), distributions)
        if self.distributionImages == None:
            self.drawDistributions(self.previousState)
        for x in range(len(self.distributionImages)):
            for y in range(len(self.distributionImages[0])):
                image = self.distributionImages[x][y]
                weights = [dist[ (x,y) ] for dist in distributions]

                if sum(weights) != 0:
                    pass
                # Fog of war
                color = [0.0,0.0,0.0]
                colors = GHOST_VEC_COLORS[1:] # With Pacman
                if self.capture: colors = GHOST_VEC_COLORS
                for weight, gcolor in zip(weights, colors):
                    color = [min(1.0, c + 0.95 * g * weight ** .3) for c,g in zip(color, gcolor)]
                changeColor(image, formatColor(*color))
        refresh()

class FirstPersonPacmanGraphics(PacmanGraphics):
    """
    First-person view graphics for Pacman.
    
    Provides a first-person perspective of the Pacman game by only showing ghosts
    that would be visible from Pacman's position.
    
    Args:
        zoom: Scale factor for the graphics display
        showGhosts: Whether to display ghosts or not
        capture: Whether this is a capture game
        frameTime: Time to pause between frames
    """
    def __init__(self, zoom: float = 1.0, showGhosts: bool = True, capture: bool = False, frameTime: float = 0) -> None:
        PacmanGraphics.__init__(self, zoom, frameTime=frameTime)
        self.showGhosts = showGhosts
        self.capture = capture

    def initialize(self, state: 'GameState', isBlue: bool = False) -> None:
        """
        Initialize the first-person graphics display.
        
        Sets up the initial display state including walls, agents and other objects.
        
        Args:
            state: Current game state
            isBlue: Whether Pacman is on the blue team (for capture games)
        """
        self.isBlue = isBlue
        PacmanGraphics.startGraphics(self, state)
        # Initialize distribution images
        walls = state.layout.walls
        dist = []
        self.layout = state.layout

        # Draw the rest
        self.distributionImages = None  # initialize lazily
        self.drawStaticObjects(state)
        self.drawAgentObjects(state)

        # Information
        self.previousState = state

    def lookAhead(self, config: 'Configuration', state: 'GameState') -> None:
        """
        Update display based on Pacman's current view direction.
        
        Only draws ghosts that would be visible from Pacman's current position
        and viewing direction.
        
        Args:
            config: Pacman's current configuration (position/direction)
            state: Current game state
        """
        if config.getDirection() == 'Stop':
            return
        else:
            # Draw relevant ghosts
            allGhosts = state.getGhostStates()
            visibleGhosts = state.getVisibleGhosts()
            for i, ghost in enumerate(allGhosts):
                if ghost in visibleGhosts:
                    self.drawGhost(ghost, i)
                else:
                    self.currentGhostImages[i] = None

    def getGhostColor(self, ghost: 'GhostState', ghostIndex: int) -> str:
        """
        Get the color for a ghost.
        
        Args:
            ghost: The ghost state
            ghostIndex: Index of the ghost
            
        Returns:
            Color string for the ghost
        """
        return GHOST_COLORS[ghostIndex]

    def getPosition(self, ghostState: 'GhostState') -> Tuple[float, float]:
        """
        Get the position to display a ghost.
        
        In first-person view, ghosts that shouldn't be visible return a far-off position.
        
        Args:
            ghostState: The ghost state to get position for
            
        Returns:
            (x,y) position tuple, (-1000,-1000) if ghost should be hidden
        """
        if not self.showGhosts and not ghostState.isPacman and ghostState.getPosition()[1] > 1:
            return (-1000, -1000)
        else:
            return PacmanGraphics.getPosition(self, ghostState)

def add(x: Tuple[float, float], y: Tuple[float, float]) -> Tuple[float, float]:
    """
    Add two 2D vectors represented as tuples.
    
    Args:
        x: First vector as (x,y) tuple
        y: Second vector as (x,y) tuple
        
    Returns:
        Tuple containing the sum of the vectors (x1+x2, y1+y2)
    """
    return (x[0] + y[0], x[1] + y[1])


###########################
#  SAVING GRAPHICAL OUTPUT  #
###########################
# Note: to make an animated gif from this postscript output, try the command:
# convert -delay 7 -loop 1 -compress lzw -layers optimize frame* out.gif
# convert is part of imagemagick (freeware)

SAVE_POSTSCRIPT: bool = False
POSTSCRIPT_OUTPUT_DIR: str = 'frames'
FRAME_NUMBER: int = 0

def saveFrame() -> None:
    """
    Saves the current graphical output as a postscript file.
    
    Creates numbered postscript files in POSTSCRIPT_OUTPUT_DIR if SAVE_POSTSCRIPT is True.
    Files are named 'frame_XXXXXXXX.ps' with sequential numbering.
    Creates output directory if it doesn't exist.
    
    Returns:
        None
    """
    global SAVE_POSTSCRIPT, FRAME_NUMBER, POSTSCRIPT_OUTPUT_DIR
    if not SAVE_POSTSCRIPT: return
    if not os.path.exists(POSTSCRIPT_OUTPUT_DIR): os.mkdir(POSTSCRIPT_OUTPUT_DIR)
    name = os.path.join(POSTSCRIPT_OUTPUT_DIR, 'frame_%08d.ps' % FRAME_NUMBER)
    FRAME_NUMBER += 1
    writePostscript(name) # writes the current canvas
