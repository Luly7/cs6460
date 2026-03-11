"""Graphics display module for Pacman game.

This module provides the graphical display functionality for the Pacman game,
including rendering of Pacman, ghosts, walls, food pellets, and other game elements.
Uses Tkinter for graphics output.

Modified by: George Rudolph at Utah Valley University
Date: 22 Nov 2024

Updates:
- Added comprehensive docstrings with Args/Returns sections
- Added type hints throughout module
- Improved code organization and readability 
- Added constants type annotations
- Added return type hints for all functions
- Added parameter type hints for all functions
- Python 3.13 compatibility verified

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


from graphicsUtils import *
import math
import time
from game import Directions

###########################
#  GRAPHICS DISPLAY CODE  #
###########################

"""
This module contains the graphics display code for the Pacman game.
Most code by Dan Klein and John Denero written or rewritten for cs188, UC Berkeley.
Some code from a Pacman implementation by LiveWires, and used / modified with permission.
"""

# Display configuration constants
DEFAULT_GRID_SIZE: float = 30.0  # Size of each grid square in pixels
INFO_PANE_HEIGHT: int = 35  # Height of information pane at bottom
BACKGROUND_COLOR: tuple[float, float, float] = formatColor(0, 0, 0)  # Black background
WALL_COLOR: tuple[float, float, float] = formatColor(0.0/255.0, 51.0/255.0, 255.0/255.0)  # Blue walls
INFO_PANE_COLOR: tuple[float, float, float] = formatColor(.4, .4, 0)  # Dark yellow info pane
SCORE_COLOR: tuple[float, float, float] = formatColor(.9, .9, .9)  # Light gray score text
PACMAN_OUTLINE_WIDTH: int = 2  # Width of Pacman outline in pixels
PACMAN_CAPTURE_OUTLINE_WIDTH: int = 4  # Width of Pacman outline in capture mode

# Ghost colors for different ghost types
GHOST_COLORS: list[tuple[float, float, float]] = []
GHOST_COLORS.append(formatColor(.9, 0, 0))  # Red
GHOST_COLORS.append(formatColor(0, .3, .9))  # Blue  
GHOST_COLORS.append(formatColor(.98, .41, .07))  # Orange
GHOST_COLORS.append(formatColor(.1, .75, .7))  # Green
GHOST_COLORS.append(formatColor(1.0, 0.6, 0.0))  # Yellow
GHOST_COLORS.append(formatColor(.4, 0.13, 0.91))  # Purple

# Team colors for capture mode (first two ghost colors)
TEAM_COLORS: list[tuple[float, float, float]] = GHOST_COLORS[:2]

# Coordinate points defining ghost shape polygon
GHOST_SHAPE: list[tuple[float, float]] = [
    (0,     0.3),
    (0.25,  0.75),
    (0.5,   0.3),
    (0.75,  0.75),
    (0.75,  -0.5),
    (0.5,   -0.75),
    (-0.5,  -0.75),
    (-0.75, -0.5),
    (-0.75, 0.75),
    (-0.5,  0.3),
    (-0.25, 0.75)
]
GHOST_SIZE: float = 0.65  # Scale factor for ghost size
SCARED_COLOR: tuple[float, float, float] = formatColor(1, 1, 1)  # White color for scared ghosts

# Pre-compute ghost colors as vectors for efficiency
GHOST_VEC_COLORS: list[tuple[float, float, float]] = list(map(colorToVector, GHOST_COLORS))

# Pacman display properties
PACMAN_COLOR: tuple[float, float, float] = formatColor(255.0/255.0, 255.0/255.0, 61.0/255)  # Yellow
PACMAN_SCALE: float = 0.5  # Scale factor for Pacman size

# Food display properties  
FOOD_COLOR: tuple[float, float, float] = formatColor(1, 1, 1)  # White
FOOD_SIZE: float = 0.1  # Scale factor for food size

# Laser display properties
LASER_COLOR: tuple[float, float, float] = formatColor(1, 0, 0)  # Red
LASER_SIZE: float = 0.02  # Scale factor for laser size

# Power capsule display properties
CAPSULE_COLOR: tuple[float, float, float] = formatColor(1, 1, 1)  # White
CAPSULE_SIZE: float = 0.25  # Scale factor for capsule size

# Wall display properties
WALL_RADIUS: float = 0.15  # Radius of wall corners

class InfoPane:
    """
    A class representing the information pane displayed at the bottom of the game window.
    Contains score, ghost distances, and team information.
    """
    def __init__(self, layout: "Layout", gridSize: float) -> None:
        """
        Initialize the info pane.

        Args:
            layout: The game layout containing dimensions
            gridSize: Size of each grid square in pixels
        """
        self.gridSize = gridSize
        self.width = (layout.width) * gridSize
        self.base = (layout.height + 1) * gridSize
        self.height = INFO_PANE_HEIGHT
        self.fontSize = 24
        self.textColor = PACMAN_COLOR
        self.drawPane()

    def toScreen(self, pos: Union[tuple[float, float], float], y: Optional[float] = None) -> tuple[float, float]:
        """
        Translates a point relative from the bottom left of the info pane to screen coordinates.

        Args:
            pos: Either an (x,y) tuple or just the x coordinate
            y: If pos is just x coordinate, this is the y coordinate

        Returns:
            tuple[float, float]: The screen coordinates (x,y)
        """
        if y == None:
            x, y = pos
        else:
            x = pos

        x = self.gridSize + x  # Margin
        y = self.base + y
        return x, y

    def drawPane(self) -> None:
        """Initialize and draw the score display text."""
        self.scoreText = text(self.toScreen(
            0, 0), self.textColor, "SCORE:    0", "Times", self.fontSize, "bold")

    def initializeGhostDistances(self, distances: list[str]) -> None:
        """
        Initialize the ghost distance displays.

        Args:
            distances: List of distance strings to display for each ghost
        """
        self.ghostDistanceText = []

        size = 20
        if self.width < 240:
            size = 12
        if self.width < 160:
            size = 10

        for i, d in enumerate(distances):
            t = text(self.toScreen(self.width/2 + self.width/8 * i, 0),
                     GHOST_COLORS[i+1], d, "Times", size, "bold")
            self.ghostDistanceText.append(t)

    def updateScore(self, score: int) -> None:
        """
        Update the displayed score.

        Args:
            score: New score to display
        """
        changeText(self.scoreText, f"SCORE: {score:4d}")

    def setTeam(self, isBlue: bool) -> None:
        """
        Set the team display text.

        Args:
            isBlue: True if blue team, False if red team
        """
        text = "RED TEAM"
        if isBlue:
            text = "BLUE TEAM"
        self.teamText = text(self.toScreen(
            300, 0), self.textColor, text, "Times", self.fontSize, "bold")

    def updateGhostDistances(self, distances: list[str]) -> None:
        """
        Update the ghost distance displays.

        Args:
            distances: List of new distance strings to display
        """
        if len(distances) == 0:
            return
        if 'ghostDistanceText' not in dir(self):
            self.initializeGhostDistances(distances)
        else:
            for i, d in enumerate(distances):
                changeText(self.ghostDistanceText[i], d)

    def drawGhost(self) -> None:
        """Draw ghost icon in the info pane."""
        pass

    def drawPacman(self) -> None:
        """Draw pacman icon in the info pane."""
        pass

    def drawWarning(self) -> None:
        """Draw warning icon in the info pane."""
        pass

    def clearIcon(self) -> None:
        """Clear any icon currently displayed in the info pane."""
        pass

    def updateMessage(self, message: str) -> None:
        """
        Update the message displayed in the info pane.

        Args:
            message: New message to display
        """
        pass

    def clearMessage(self) -> None:
        """Clear the message currently displayed in the info pane."""
        pass


class PacmanGraphics:
    def __init__(self, zoom: float = 1.0, frameTime: float = 0.0, capture: bool = False) -> None:
        """
        Initialize the Pacman graphics display.

        Args:
            zoom: Scale factor for the display size
            frameTime: Time between animation frames in seconds
            capture: Whether this is a capture game display
        """
        self.have_window = 0
        self.currentGhostImages = {}
        self.pacmanImage = None
        self.zoom = zoom
        self.gridSize = DEFAULT_GRID_SIZE * zoom
        self.capture = capture
        self.frameTime = frameTime

    def checkNullDisplay(self) -> bool:
        """Check if display is null/disabled."""
        return False

    def initialize(self, state, isBlue: bool = False) -> None:
        """
        Initialize the game display with the given state.

        Args:
            state: Initial game state to display
            isBlue: Whether this is the blue team's perspective
        """
        self.isBlue = isBlue
        self.startGraphics(state)

        # self.drawDistributions(state)
        self.distributionImages = None  # Initialized lazily
        self.drawStaticObjects(state)
        self.drawAgentObjects(state)

        # Information
        self.previousState = state

    def startGraphics(self, state) -> None:
        """
        Start up the graphics display for the given game state.

        Args:
            state: Game state to initialize display with
        """
        self.layout = state.layout
        layout = self.layout
        self.width = layout.width
        self.height = layout.height
        self.make_window(self.width, self.height)
        self.infoPane = InfoPane(layout, self.gridSize)
        self.currentState = layout

    def drawDistributions(self, state) -> None:
        """
        Draw the belief distributions for the agents.

        Args:
            state: Current game state
        """
        walls = state.layout.walls
        dist = []
        for x in range(walls.width):
            distx = []
            dist.append(distx)
            for y in range(walls.height):
                (screen_x, screen_y) = self.to_screen((x, y))
                block = square((screen_x, screen_y),
                               0.5 * self.gridSize,
                               color=BACKGROUND_COLOR,
                               filled=1, behind=2)
                distx.append(block)
        self.distributionImages = dist

    def drawStaticObjects(self, state) -> None:
        """
        Draw the static game objects (walls, food, capsules).

        Args:
            state: Current game state
        """
        layout = self.layout
        self.drawWalls(layout.walls)
        self.food = self.drawFood(layout.food)
        self.capsules = self.drawCapsules(layout.capsules)
        refresh()

    def drawAgentObjects(self, state) -> None:
        """
        Draw all agent objects (Pacman and ghosts).

        Args:
            state: Current game state
        """
        self.agentImages = []  # (agentState, image)
        for index, agent in enumerate(state.agentStates):
            if agent.isPacman:
                image = self.drawPacman(agent, index)
                self.agentImages.append((agent, image))
            else:
                image = self.drawGhost(agent, index)
                self.agentImages.append((agent, image))
        refresh()

    def swapImages(self, agentIndex: int, newState) -> None:
        """
        Changes an image from a ghost to a pacman or vice versa (for capture).

        Args:
            agentIndex: Index of agent to swap
            newState: New agent state
        """
        prevState, prevImage = self.agentImages[agentIndex]
        for item in prevImage:
            remove_from_screen(item)
        if newState.isPacman:
            image = self.drawPacman(newState, agentIndex)
            self.agentImages[agentIndex] = (newState, image)
        else:
            image = self.drawGhost(newState, agentIndex)
            self.agentImages[agentIndex] = (newState, image)
        refresh()

    def update(self, newState) -> None:
        """
        Update the display for a new game state.

        Args:
            newState: New game state to display
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
        Create the graphics window.

        Args:
            width: Width of window in grid cells
            height: Height of window in grid cells
        """
        grid_width = (width-1) * self.gridSize
        grid_height = (height-1) * self.gridSize
        screen_width = 2*self.gridSize + grid_width
        screen_height = 2*self.gridSize + grid_height + INFO_PANE_HEIGHT

        begin_graphics(screen_width,
                       screen_height,
                       BACKGROUND_COLOR,
                       "CS188 Pacman")

    def drawPacman(self, pacman, index: int) -> list:
        """
        Draw a Pacman agent.

        Args:
            pacman: Pacman agent state
            index: Index of the agent

        Returns:
            List containing the Pacman graphics object
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
                       fillColor=fillColor, outlineColor=outlineColor,
                       endpoints=endpoints,
                       width=width)]

    def getEndpoints(self, direction: str, position: tuple[float, float] = (0, 0)) -> tuple[float, float]:
        """
        Get the endpoints of the Pacman mouth arc.

        Args:
            direction: Direction Pacman is facing
            position: Position of Pacman

        Returns:
            Tuple of start and end angles for mouth arc
        """
        x, y = position
        pos = x - int(x) + y - int(y)
        width = 30 + 80 * math.sin(math.pi * pos)

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

    def movePacman(self, position: tuple[float, float], direction: str, image: list) -> None:
        """
        Move the Pacman graphics to a new position.

        Args:
            position: New position
            direction: New direction
            image: Pacman graphics object
        """
        screenPosition = self.to_screen(position)
        endpoints = self.getEndpoints(direction, position)
        r = PACMAN_SCALE * self.gridSize
        moveCircle(image[0], screenPosition, r, endpoints)
        refresh()

    def animatePacman(self, pacman, prevPacman, image: list) -> None:
        """
        Animate Pacman moving between positions.

        Args:
            pacman: New Pacman state
            prevPacman: Previous Pacman state
            image: Pacman graphics object
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
            for i in range(1, int(frames) + 1):
                pos = px*i/frames + fx * \
                    (frames-i)/frames, py*i/frames + fy*(frames-i)/frames
                self.movePacman(pos, self.getDirection(pacman), image)
                refresh()
                sleep(abs(self.frameTime) / frames)
        else:
            self.movePacman(self.getPosition(pacman),
                            self.getDirection(pacman), image)
        refresh()

    def getGhostColor(self, ghost: 'AgentState', ghostIndex: int) -> tuple[float, float, float]:
        """
        Get the color for a ghost.

        Args:
            ghost: Ghost agent state
            ghostIndex: Index of the ghost

        Returns:
            RGB color tuple
        """
        if ghost.scaredTimer > 0:
            return SCARED_COLOR
        else:
            return GHOST_COLORS[ghostIndex]

    def drawGhost(self, ghost: 'AgentState', agentIndex: int) -> list:
        """
        Draw a ghost.

        Args:
            ghost: Ghost agent state
            agentIndex: Index of the ghost

        Returns:
            List of ghost graphics objects
        """
        pos = self.getPosition(ghost)
        dir = self.getDirection(ghost)
        (screen_x, screen_y) = (self.to_screen(pos))
        coords = []
        for (x, y) in GHOST_SHAPE:
            coords.append((x*self.gridSize*GHOST_SIZE + screen_x,
                           y*self.gridSize*GHOST_SIZE + screen_y))

        colour = self.getGhostColor(ghost, agentIndex)
        body = polygon(coords, colour, filled=1)
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
        leftEye = circle((screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx/1.5), screen_y -
                          self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2, WHITE, WHITE)
        rightEye = circle((screen_x+self.gridSize*GHOST_SIZE*(0.3+dx/1.5), screen_y -
                           self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2, WHITE, WHITE)
        leftPupil = circle((screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx), screen_y -
                            self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08, BLACK, BLACK)
        rightPupil = circle((screen_x+self.gridSize*GHOST_SIZE*(0.3+dx), screen_y -
                             self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08, BLACK, BLACK)
        ghostImageParts = []
        ghostImageParts.append(body)
        ghostImageParts.append(leftEye)
        ghostImageParts.append(rightEye)
        ghostImageParts.append(leftPupil)
        ghostImageParts.append(rightPupil)

        return ghostImageParts

    def moveEyes(self, pos: tuple[float, float], dir: str, eyes: list) -> None:
        """
        Move the ghost's eyes.

        Args:
            pos: New position
            dir: New direction
            eyes: List of eye graphics objects
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
        moveCircle(eyes[0], (screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx/1.5), screen_y -
                             self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2)
        moveCircle(eyes[1], (screen_x+self.gridSize*GHOST_SIZE*(0.3+dx/1.5), screen_y -
                             self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2)
        moveCircle(eyes[2], (screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx), screen_y -
                             self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08)
        moveCircle(eyes[3], (screen_x+self.gridSize*GHOST_SIZE*(0.3+dx), screen_y -
                             self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08)

    def moveGhost(self, ghost: 'AgentState', ghostIndex: int, prevGhost: 'AgentState', ghostImageParts: list) -> None:
        """
        Move a ghost to a new position.

        Args:
            ghost: New ghost state
            ghostIndex: Index of the ghost
            prevGhost: Previous ghost state
            ghostImageParts: List of ghost graphics objects
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
        self.moveEyes(self.getPosition(ghost),
                      self.getDirection(ghost), ghostImageParts[-4:])
        refresh()

    def getPosition(self, agentState: 'AgentState') -> tuple[float, float]:
        """
        Get the position of an agent.

        Args:
            agentState: Agent state

        Returns:
            Position tuple (x,y)
        """
        if agentState.configuration == None:
            return (-1000, -1000)
        return agentState.getPosition()

    def getDirection(self, agentState: 'AgentState') -> str:
        """
        Get the direction of an agent.

        Args:
            agentState: Agent state

        Returns:
            Direction string
        """
        if agentState.configuration == None:
            return Directions.STOP
        return agentState.configuration.getDirection()

    def finish(self) -> None:
        """Clean up graphics display."""
        end_graphics()

    def to_screen(self, point: tuple[float, float]) -> tuple[float, float]:
        """
        Convert a game coordinate to a screen coordinate.

        Args:
            point: Game coordinate (x,y)

        Returns:
            Screen coordinate tuple
        """
        (x, y) = point
        #y = self.height - y
        x = (x + 1)*self.gridSize
        y = (self.height - y)*self.gridSize
        return (x, y)

    def to_screen2(self, point: tuple[float, float]) -> tuple[float, float]:
        """
        Convert a game coordinate to a screen coordinate (alternate version).
        Fixes some TK issue with off-center circles.

        Args:
            point: Game coordinate (x,y)

        Returns:
            Screen coordinate tuple
        """
        (x, y) = point
        #y = self.height - y
        x = (x + 1)*self.gridSize
        y = (self.height - y)*self.gridSize
        return (x, y)

    def drawWalls(self, wallMatrix: 'Grid') -> None:
        """
        Draw the maze walls.

        Args:
            wallMatrix: Grid of wall locations
        """
        wallColor = WALL_COLOR
        for xNum, x in enumerate(wallMatrix):
            if self.capture and (xNum * 2) < wallMatrix.width:
                wallColor = TEAM_COLORS[0]
            if self.capture and (xNum * 2) >= wallMatrix.width:
                wallColor = TEAM_COLORS[1]

            for yNum, cell in enumerate(x):
                if cell:  # There's a wall here
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
                        circle(screen2, WALL_RADIUS * self.gridSize,
                               wallColor, wallColor, (0, 91), 'arc')
                    if (nIsWall) and (not eIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize*WALL_RADIUS, 0)), add(screen,
                                                                              (self.gridSize*WALL_RADIUS, self.gridSize*(-0.5)-1)), wallColor)
                    if (not nIsWall) and (eIsWall):
                        # horizontal line
                        line(add(screen, (0, self.gridSize*(-1)*WALL_RADIUS)), add(screen,
                                                                                   (self.gridSize*0.5+1, self.gridSize*(-1)*WALL_RADIUS)), wallColor)
                    if (nIsWall) and (eIsWall) and (not neIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize*2*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS)),
                               WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (180, 271), 'arc')
                        line(add(screen, (self.gridSize*2*WALL_RADIUS-1, self.gridSize*(-1)*WALL_RADIUS)),
                             add(screen, (self.gridSize*0.5+1, self.gridSize*(-1)*WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS+1)),
                             add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(-0.5))), wallColor)

                    # NW quadrant
                    if (not nIsWall) and (not wIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize,
                               wallColor, wallColor, (90, 181), 'arc')
                    if (nIsWall) and (not wIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, 0)), add(screen,
                                                                                   (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(-0.5)-1)), wallColor)
                    if (not nIsWall) and (wIsWall):
                        # horizontal line
                        line(add(screen, (0, self.gridSize*(-1)*WALL_RADIUS)), add(screen,
                                                                                   (self.gridSize*(-0.5)-1, self.gridSize*(-1)*WALL_RADIUS)), wallColor)
                    if (nIsWall) and (wIsWall) and (not nwIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize*(-2)*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS)),
                               WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (270, 361), 'arc')
                        line(add(screen, (self.gridSize*(-2)*WALL_RADIUS+1, self.gridSize*(-1)*WALL_RADIUS)),
                             add(screen, (self.gridSize*(-0.5), self.gridSize*(-1)*WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS+1)),
                             add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(-0.5))), wallColor)

                    # SE quadrant
                    if (not sIsWall) and (not eIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize,
                               wallColor, wallColor, (270, 361), 'arc')
                    if (sIsWall) and (not eIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize*WALL_RADIUS, 0)), add(screen,
                                                                              (self.gridSize*WALL_RADIUS, self.gridSize*(0.5)+1)), wallColor)
                    if (not sIsWall) and (eIsWall):
                        # horizontal line
                        line(add(screen, (0, self.gridSize*(1)*WALL_RADIUS)), add(screen,
                                                                                  (self.gridSize*0.5+1, self.gridSize*(1)*WALL_RADIUS)), wallColor)
                    if (sIsWall) and (eIsWall) and (not seIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize*2*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS)),
                               WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (90, 181), 'arc')
                        line(add(screen, (self.gridSize*2*WALL_RADIUS-1, self.gridSize*(1)*WALL_RADIUS)),
                             add(screen, (self.gridSize*0.5, self.gridSize*(1)*WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS-1)),
                             add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(0.5))), wallColor)

                    # SW quadrant
                    if (not sIsWall) and (not wIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize,
                               wallColor, wallColor, (180, 271), 'arc')
                    if (sIsWall) and (not wIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, 0)), add(screen,
                                                                                   (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(0.5)+1)), wallColor)
                    if (not sIsWall) and (wIsWall):
                        # horizontal line
                        line(add(screen, (0, self.gridSize*(1)*WALL_RADIUS)), add(screen,
                                                                                  (self.gridSize*(-0.5)-1, self.gridSize*(1)*WALL_RADIUS)), wallColor)
                    if (sIsWall) and (wIsWall) and (not swIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize*(-2)*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS)),
                               WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (0, 91), 'arc')
                        line(add(screen, (self.gridSize*(-2)*WALL_RADIUS+1, self.gridSize*(1)*WALL_RADIUS)),
                             add(screen, (self.gridSize*(-0.5), self.gridSize*(1)*WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS-1)),
                             add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(0.5))), wallColor)

    def isWall(self, x: int, y: int, walls: 'Grid') -> bool:
        """
        Check if there is a wall at the given position.

        Args:
            x: X coordinate
            y: Y coordinate
            walls: Grid of wall locations

        Returns:
            True if there is a wall, False otherwise
        """
        if x < 0 or y < 0:
            return False
        if x >= walls.width or y >= walls.height:
            return False
        return walls[x][y]

    def drawFood(self, foodMatrix: 'Grid') -> list[list]:
        """
        Draw all food dots.

        Args:
            foodMatrix: Grid of food locations

        Returns:
            2D list of food graphics objects
        """
        foodImages = []
        color = FOOD_COLOR
        for xNum, x in enumerate(foodMatrix):
            if self.capture and (xNum * 2) <= foodMatrix.width:
                color = TEAM_COLORS[0]
            if self.capture and (xNum * 2) > foodMatrix.width:
                color = TEAM_COLORS[1]
            imageRow = []
            foodImages.append(imageRow)
            for yNum, cell in enumerate(x):
                if cell:  # There's food here
                    screen = self.to_screen((xNum, yNum))
                    dot = circle(screen,
                                 FOOD_SIZE * self.gridSize,
                                 outlineColor=color, fillColor=color,
                                 width=1)
                    imageRow.append(dot)
                else:
                    imageRow.append(None)
        return foodImages

    def drawCapsules(self, capsules: list[tuple[int, int]]) -> dict:
        """
        Draw all capsules.

        Args:
            capsules: List of capsule positions

        Returns:
            Dictionary mapping positions to capsule graphics objects
        """
        capsuleImages = {}
        for capsule in capsules:
            (screen_x, screen_y) = self.to_screen(capsule)
            dot = circle((screen_x, screen_y),
                         CAPSULE_SIZE * self.gridSize,
                         outlineColor=CAPSULE_COLOR,
                         fillColor=CAPSULE_COLOR,
                         width=1)
            capsuleImages[capsule] = dot
        return capsuleImages

    def removeFood(self, cell: tuple[int, int], foodImages: list[list]) -> None:
        """
        Remove a food dot from display.

        Args:
            cell: Position of food to remove
            foodImages: 2D list of food graphics objects
        """
        x, y = cell
        remove_from_screen(foodImages[x][y])

    def removeCapsule(self, cell: tuple[int, int], capsuleImages: dict) -> None:
        """
        Remove a capsule from display.

        Args:
            cell: Position of capsule to remove
            capsuleImages: Dictionary of capsule graphics objects
        """
        x, y = cell
        remove_from_screen(capsuleImages[(x, y)])

    def drawExpandedCells(self, cells: list[tuple[int, int]]) -> None:
        """
        Draw an overlay of expanded grid positions for search agents.

        Args:
            cells: List of cell positions to highlight
        """
        n = float(len(cells))
        baseColor = [1.0, 0.0, 0.0]
        self.clearExpandedCells()
        self.expandedCells = []
        for k, cell in enumerate(cells):
            screenPos = self.to_screen(cell)
            cellColor = formatColor(
                *[(n-k) * c * .5 / n + .25 for c in baseColor])
            block = square(screenPos,
                           0.5 * self.gridSize,
                           color=cellColor,
                           filled=1, behind=2)
            self.expandedCells.append(block)
            if self.frameTime < 0:
                refresh()

    def clearExpandedCells(self):
        if 'expandedCells' in dir(self) and len(self.expandedCells) > 0:
            for cell in self.expandedCells:
                remove_from_screen(cell)

    def updateDistributions(self, distributions):
        "Draws an agent's belief distributions"
        # copy all distributions so we don't change their state
        distributions = [x.copy() for x in distributions]
        if self.distributionImages == None:
            self.drawDistributions(self.previousState)
        for x in range(len(self.distributionImages)):
            for y in range(len(self.distributionImages[0])):
                image = self.distributionImages[x][y]
                weights = [dist[(x, y)] for dist in distributions]

                if sum(weights) != 0:
                    pass
                # Fog of war
                color = [0.0, 0.0, 0.0]
                colors = GHOST_VEC_COLORS[1:]  # With Pacman
                if self.capture:
                    colors = GHOST_VEC_COLORS
                for weight, gcolor in zip(weights, colors):
                    color = [min(1.0, c + 0.95 * g * weight ** .3)
                             for c, g in zip(color, gcolor)]
                changeColor(image, formatColor(*color))
        refresh()


class FirstPersonPacmanGraphics(PacmanGraphics):
    """
    First-person view graphics for Pacman game.
    
    Provides a first-person perspective of the Pacman game world, showing only what would be
    visible from Pacman's point of view.
    
    Args:
        zoom: Scale factor for the display (default 1.0)
        showGhosts: Whether to show ghosts in the display (default True)
        capture: Whether this is capture mode (default False) 
        frameTime: Time between frames in seconds (default 0)
    """
    def __init__(self, zoom: float = 1.0, showGhosts: bool = True, capture: bool = False, frameTime: float = 0) -> None:
        PacmanGraphics.__init__(self, zoom, frameTime=frameTime)
        self.showGhosts = showGhosts
        self.capture = capture

    def initialize(self, state: 'GameState', isBlue: bool = False) -> None:
        """
        Initialize the first-person display.
        
        Sets up the initial game state and graphics for first-person view.
        
        Args:
            state: Current game state
            isBlue: Whether Pacman is on blue team (default False)
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
        
        Shows only ghosts that would be visible from Pacman's current position and direction.
        
        Args:
            config: Pacman's current configuration (position/direction)
            state: Current game state
        """
        if config.getDirection() == 'Stop':
            return
        else:
            pass
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
        Get the display position for a ghost.
        
        In first-person view, ghosts that shouldn't be visible return far off-screen.
        
        Args:
            ghostState: State of the ghost
            
        Returns:
            (x,y) position tuple, (-1000,-1000) if ghost should be hidden
        """
        if not self.showGhosts and not ghostState.isPacman and ghostState.getPosition()[1] > 1:
            return (-1000, -1000)
        else:
            return PacmanGraphics.getPosition(self, ghostState)


def add(x: Tuple[float, float], y: Tuple[float, float]) -> Tuple[float, float]:
    """
    Add two 2D vectors.
    
    Args:
        x: First vector as (x,y) tuple
        y: Second vector as (x,y) tuple
        
    Returns:
        Sum vector as (x,y) tuple
    """
    return (x[0] + y[0], x[1] + y[1])

###############################################################################
#                         SAVING GRAPHICAL OUTPUT                               #
# Note: to make an animated gif from this postscript output, try the command:  #
# convert -delay 7 -loop 1 -compress lzw -layers optimize frame* out.gif       #
# convert is part of imagemagick (freeware)                                    #
###############################################################################

SAVE_POSTSCRIPT: bool = False
POSTSCRIPT_OUTPUT_DIR: str = 'frames'
FRAME_NUMBER: int = 0
import os


def saveFrame() -> None:
    """
    Save the current graphical output as a postscript file.
    
    If SAVE_POSTSCRIPT is enabled, saves the current canvas state as a numbered
    postscript file in the POSTSCRIPT_OUTPUT_DIR directory. Files are named
    sequentially as frame_XXXXXXXX.ps where XXXXXXXX is the frame number.
    
    Creates the output directory if it doesn't exist.
    
    Global variables used:
        SAVE_POSTSCRIPT: Whether to save frames
        FRAME_NUMBER: Current frame number, incremented after each save
        POSTSCRIPT_OUTPUT_DIR: Directory to save frames in
    """
    global SAVE_POSTSCRIPT, FRAME_NUMBER, POSTSCRIPT_OUTPUT_DIR
    if not SAVE_POSTSCRIPT:
        return
    if not os.path.exists(POSTSCRIPT_OUTPUT_DIR):
        os.mkdir(POSTSCRIPT_OUTPUT_DIR)
    name = os.path.join(POSTSCRIPT_OUTPUT_DIR, 'frame_%08d.ps' % FRAME_NUMBER)
    FRAME_NUMBER += 1
    writePostscript(name)  # writes the current canvas
