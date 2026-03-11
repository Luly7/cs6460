"""Core game logic module for Pacman AI projects.

This module provides the foundational game mechanics and data structures for the Pacman game,
including agents, game states, rules, and movement logic.

Modified by: George Rudolph at Utah Valley University
Date: 22 Nov 2024

Updates:
- Added comprehensive docstrings with Args/Returns sections
- Added type hints throughout module
- Improved code organization and readability
- Added constants type annotations
- Added return type hints for all functions
- Added parameter type hints for all functions
- Use f-strings for improved readability
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

import abc
from util import *
import time
import os
import traceback
import sys

#######################
# Parts worth reading #
#######################


class Agent(metaclass=abc.ABCMeta):
    """
    Base class for all agents in the game.

    An agent must define a getAction method to determine its behavior. May also optionally
    define a registerInitialState method to inspect the starting state.

    Attributes:
        index: Integer identifying which agent this is in the game
    """

    def __init__(self, index: int = 0) -> None:
        self.index = index

    @abc.abstractmethod
    def getAction(self, state: 'GameState') -> str:
        """
        Determine the agent's action based on the current game state.

        Args:
            state: Current GameState object representing game state

        Returns:
            Action string from Directions.{North, South, East, West, Stop}
        """
        return


class Directions:
    """
    Constants and mappings for movement directions in the game.

    Contains direction constants and mappings between directions for turning left/right
    and reversing direction.
    """
    NORTH = 'North'
    SOUTH = 'South'
    EAST = 'East'
    WEST = 'West'
    STOP = 'Stop'

    LEFT = {NORTH: WEST,
            SOUTH: EAST,
            EAST:  NORTH,
            WEST:  SOUTH,
            STOP:  STOP}

    RIGHT = dict([(y, x) for x, y in list(LEFT.items())])

    REVERSE = {NORTH: SOUTH,
               SOUTH: NORTH,
               EAST: WEST,
               WEST: EAST,
               STOP: STOP}


class Configuration:
    """
    Stores position and direction information for game characters.

    The convention for positions is that (0,0) is the lower left corner, with x increasing
    horizontally and y increasing vertically. North is the direction of increasing y (0,1).

    Attributes:
        pos: Tuple of (x,y) coordinates
        direction: String indicating direction of travel from Directions constants
    """

    def __init__(self, pos: tuple[float, float], direction: str) -> None:
        self.pos = pos
        self.direction = direction

    def getPosition(self) -> tuple[float, float]:
        """Get the current position coordinates."""
        return self.pos

    def getDirection(self) -> str:
        """Get the current direction of travel."""
        return self.direction

    def isInteger(self) -> bool:
        """Check if position coordinates are integer values."""
        x, y = self.pos
        return x == int(x) and y == int(y)

    def __eq__(self, other: 'Configuration') -> bool:
        if other == None:
            return False
        return (self.pos == other.pos and self.direction == other.direction)

    def __hash__(self) -> int:
        x = hash(self.pos)
        y = hash(self.direction)
        return hash(x + 13 * y)

    def __str__(self) -> str:
        return f"(x,y)={str(self.pos)}, {str(self.direction)}"

    def generateSuccessor(self, vector: tuple[float, float]) -> 'Configuration':
        """
        Generate new configuration after moving by the given vector.

        Args:
            vector: Movement vector as (dx,dy) tuple

        Returns:
            New Configuration after applying movement vector

        Note: This is a low-level call that does not check movement legality.
        """
        x, y = self.pos
        dx, dy = vector
        direction = Actions.vectorToDirection(vector)
        if direction == Directions.STOP:
            direction = self.direction  # There is no stop direction
        return Configuration((x + dx, y+dy), direction)

class AgentState:
    """
    AgentStates hold the state of an agent (configuration, speed, scared, etc).
    
    Attributes:
        start: Initial configuration of the agent
        configuration: Current configuration of the agent 
        isPacman: Boolean indicating if agent is Pacman (True) or Ghost (False)
        scaredTimer: Time remaining in scared state
        numCarrying: Number of food pellets being carried (contest only)
        numReturned: Number of food pellets returned to start (contest only)
    """

    def __init__(self, startConfiguration: 'Configuration', isPacman: bool) -> None:
        """
        Initialize agent state.
        
        Args:
            startConfiguration: Initial configuration of the agent
            isPacman: Whether this agent is Pacman (True) or a ghost (False)
        """
        self.start = startConfiguration
        self.configuration = startConfiguration
        self.isPacman = isPacman
        self.scaredTimer = 0
        # state below potentially used for contest only
        self.numCarrying = 0
        self.numReturned = 0

    def __str__(self) -> str:
        """Return string representation of agent state."""
        if self.isPacman:
            return f"Pacman: {self.configuration}"
        else:
            return f"Ghost: {self.configuration}"

    def __eq__(self, other: 'AgentState') -> bool:
        """Check if two agent states are equal."""
        if other == None:
            return False
        return self.configuration == other.configuration and self.scaredTimer == other.scaredTimer

    def __hash__(self) -> int:
        """Generate hash value for agent state."""
        return hash(hash(self.configuration) + 13 * hash(self.scaredTimer))

    def copy(self) -> 'AgentState':
        """Return a deep copy of this agent state."""
        state = AgentState(self.start, self.isPacman)
        state.configuration = self.configuration
        state.scaredTimer = self.scaredTimer
        state.numCarrying = self.numCarrying
        state.numReturned = self.numReturned
        return state

    def getPosition(self) -> tuple[float, float] | None:
        """Get current position of agent, or None if no configuration exists."""
        if self.configuration == None:
            return None
        return self.configuration.getPosition()

    def getDirection(self) -> str:
        """Get current direction of agent."""
        return self.configuration.getDirection()

class Grid:
    """
    A 2-dimensional array of objects backed by a list of lists.
    
    Data is accessed via grid[x][y] where (x,y) are positions on a Pacman map with x horizontal,
    y vertical and the origin (0,0) in the bottom left corner. The grid can only contain boolean values.
    The __str__ method constructs an output that is oriented like a pacman board.
    
    Attributes:
        width: Width of the grid in cells
        height: Height of the grid in cells
        data: 2D list storing the grid values
        CELLS_PER_INT: Number of cells that can be packed into one integer
    """

    def __init__(self, width: int, height: int, initialValue: bool = False, bitRepresentation: tuple[int, ...] | None = None) -> None:
        if initialValue not in [False, True]:
            raise Exception('Grids can only contain booleans')
        self.CELLS_PER_INT = 30

        self.width = width
        self.height = height
        self.data = [[initialValue for y in range(
            height)] for x in range(width)]
        if bitRepresentation:
            self._unpackBits(bitRepresentation)

    def __getitem__(self, i: int) -> list[bool]:
        return self.data[i]

    def __setitem__(self, key: int, item: list[bool]) -> None:
        self.data[key] = item

    def __str__(self) -> str:
        out = [[str(self.data[x][y])[0] for x in range(self.width)]
               for y in range(self.height)]
        out.reverse()
        return '\n'.join([''.join(x) for x in out])

    def __eq__(self, other: 'Grid') -> bool:
        if other == None:
            return False
        return self.data == other.data

    def __hash__(self) -> int:
        # return hash(str(self))
        base = 1
        h = 0
        for l in self.data:
            for i in l:
                if i:
                    h += base
                base *= 2
        return hash(h)

    def copy(self) -> 'Grid':
        """Return a deep copy of this grid."""
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deepCopy(self) -> 'Grid':
        """Return a deep copy of this grid."""
        return self.copy()

    def shallowCopy(self) -> 'Grid':
        """Return a shallow copy of this grid."""
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    def count(self, item: bool = True) -> int:
        """Count number of cells matching the given value."""
        return sum([x.count(item) for x in self.data])

    def asList(self, key: bool = True) -> list[tuple[int, int]]:
        """Return list of (x,y) coordinates of cells matching the given value."""
        list = []
        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] == key:
                    list.append((x, y))
        return list

    def packBits(self) -> tuple[int, ...]:
        """
        Returns an efficient int list representation.

        Returns:
            Tuple of (width, height, bitPackedInts...)
        """
        bits = [self.width, self.height]
        currentInt = 0
        for i in range(self.height * self.width):
            bit = self.CELLS_PER_INT - (i % self.CELLS_PER_INT) - 1
            x, y = self._cellIndexToPosition(i)
            if self[x][y]:
                currentInt += 2 ** bit
            if (i + 1) % self.CELLS_PER_INT == 0:
                bits.append(currentInt)
                currentInt = 0
        bits.append(currentInt)
        return tuple(bits)

    def _cellIndexToPosition(self, index: int) -> tuple[int, int]:
        """Convert cell index to (x,y) position."""
        x = index / self.height
        y = index % self.height
        return x, y

    def _unpackBits(self, bits: tuple[int, ...]) -> None:
        """
        Fills in data from a bit-level representation.
        
        Args:
            bits: Tuple of integers containing packed bit data
        """
        cell = 0
        for packed in bits:
            for bit in self._unpackInt(packed, self.CELLS_PER_INT):
                if cell == self.width * self.height:
                    break
                x, y = self._cellIndexToPosition(cell)
                self[x][y] = bit
                cell += 1

    def _unpackInt(self, packed: int, size: int) -> list[bool]:
        """
        Unpack an integer into a list of booleans.
        
        Args:
            packed: Integer to unpack
            size: Number of bits to unpack
            
        Returns:
            List of booleans representing the bits
            
        Raises:
            ValueError: If packed integer is negative
        """
        bools = []
        if packed < 0:
            raise ValueError("must be a positive integer")
        for i in range(size):
            n = 2 ** (self.CELLS_PER_INT - i - 1)
            if packed >= n:
                bools.append(True)
                packed -= n
            else:
                bools.append(False)
        return bools


def reconstituteGrid(bitRep: tuple[int, ...]) -> 'Grid':
    """
    Reconstruct a Grid object from its bit representation.
    
    Args:
        bitRep: Either a tuple containing the bit representation or an existing Grid
        
    Returns:
        Grid object reconstructed from the bit representation, or the original Grid if passed
    """
    if type(bitRep) is not type((1, 2)):
        return bitRep
    width, height = bitRep[:2]
    return Grid(width, height, bitRepresentation=bitRep[2:])

####################################
# Parts you shouldn't have to read #
####################################


class Actions:
    """
    A collection of static methods for manipulating move actions.
    
    Provides utilities for working with movement directions, vectors, and legal moves.
    
    Attributes:
        _directions: Dict mapping direction names to (dx,dy) vectors
        _directionsAsList: List of (direction name, vector) tuples
        TOLERANCE: Float threshold for position comparisons
    """
    # Directions
    _directions = {Directions.WEST:  (-1, 0),
                   Directions.STOP:  (0, 0),
                   Directions.EAST:  (1, 0),
                   Directions.NORTH: (0, 1),
                   Directions.SOUTH: (0, -1)}

    _directionsAsList = [('West', (-1, 0)), ('Stop', (0, 0)), ('East', (1, 0)), ('North', (0, 1)), ('South', (0, -1))]

    TOLERANCE = .001

    def reverseDirection(action: str) -> str:
        """
        Get the opposite direction of the given action.
        
        Args:
            action: Direction string to reverse
            
        Returns:
            String representing opposite direction
        """
        if action == Directions.NORTH:
            return Directions.SOUTH
        if action == Directions.SOUTH:
            return Directions.NORTH
        if action == Directions.EAST:
            return Directions.WEST
        if action == Directions.WEST:
            return Directions.EAST
        return action
    reverseDirection = staticmethod(reverseDirection)

    def vectorToDirection(vector: tuple[float, float]) -> str:
        """
        Convert a movement vector to a direction string.
        
        Args:
            vector: (dx,dy) movement vector
            
        Returns:
            Direction string corresponding to vector
        """
        dx, dy = vector
        if dy > 0:
            return Directions.NORTH
        if dy < 0:
            return Directions.SOUTH
        if dx < 0:
            return Directions.WEST
        if dx > 0:
            return Directions.EAST
        return Directions.STOP
    vectorToDirection = staticmethod(vectorToDirection)

    def directionToVector(direction: str, speed: float = 1.0) -> tuple[float, float]:
        """
        Convert a direction string to a movement vector.
        
        Args:
            direction: Direction string to convert
            speed: Scalar multiplier for vector magnitude
            
        Returns:
            (dx,dy) movement vector scaled by speed
        """
        dx, dy = Actions._directions[direction]
        return (dx * speed, dy * speed)
    directionToVector = staticmethod(directionToVector)

    def getPossibleActions(config: 'Configuration', walls: 'Grid') -> list[str]:
        """
        Get list of possible movement actions from current configuration.
        
        Args:
            config: Current Configuration object
            walls: Grid of wall positions
            
        Returns:
            List of legal direction strings
        """
        possible = []
        x, y = config.pos
        x_int, y_int = int(x + 0.5), int(y + 0.5)

        # In between grid points, all agents must continue straight
        if (abs(x - x_int) + abs(y - y_int) > Actions.TOLERANCE):
            return [config.getDirection()]

        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_y = y_int + dy
            next_x = x_int + dx
            if not walls[next_x][next_y]:
                possible.append(dir)

        return possible

    getPossibleActions = staticmethod(getPossibleActions)

    def getLegalNeighbors(position: tuple[float, float], walls: 'Grid') -> list[tuple[int, int]]:
        """
        Get list of legal neighboring positions.
        
        Args:
            position: Current (x,y) position
            walls: Grid of wall positions
            
        Returns:
            List of legal (x,y) neighbor positions
        """
        x, y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []
        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_x = x_int + dx
            if next_x < 0 or next_x == walls.width:
                continue
            next_y = y_int + dy
            if next_y < 0 or next_y == walls.height:
                continue
            if not walls[next_x][next_y]:
                neighbors.append((next_x, next_y))
        return neighbors
    getLegalNeighbors = staticmethod(getLegalNeighbors)

    def getSuccessor(position: tuple[float, float], action: str) -> tuple[float, float]:
        """
        Get resulting position after taking an action.
        
        Args:
            position: Current (x,y) position
            action: Direction string to move
            
        Returns:
            New (x,y) position after taking action
        """
        dx, dy = Actions.directionToVector(action)
        x, y = position
        return (x + dx, y + dy)
    getSuccessor = staticmethod(getSuccessor)


class GameStateData:
    """
    Data structure containing the complete game state.
    
    Stores information about food, capsules, agent positions/states, score,
    and game status flags. Can be copied and compared.
    
    Attributes:
        food: Grid of food pellet positions
        capsules: List of power pellet positions
        agentStates: List of AgentState objects for all agents
        layout: Layout object containing walls and initial positions
        score: Current game score
        scoreChange: Change in score from last state
        _foodEaten: Position of food pellet eaten in last move
        _foodAdded: Position of food pellet added in last move  
        _capsuleEaten: Position of capsule eaten in last move
        _agentMoved: Index of agent that moved in last move
        _lose: Whether game is lost
        _win: Whether game is won
    """

    def __init__(self, prevState = None):
        """
        Initialize game state, optionally copying from previous state.
        
        Args:
            prevState: Previous GameStateData to copy from, or None for new state
        """
        if prevState != None:
            self.food = prevState.food.shallowCopy()
            self.capsules = prevState.capsules[:]
            self.agentStates = self.copyAgentStates(prevState.agentStates)
            self.layout = prevState.layout
            self._eaten = prevState._eaten
            self.score = prevState.score

        self._foodEaten = None
        self._foodAdded = None
        self._capsuleEaten = None
        self._agentMoved = None
        self._lose = False
        self._win = False
        self.scoreChange = 0

    def deepCopy(self) -> 'GameStateData':
        """Create a deep copy of the game state."""
        state = GameStateData(self)
        state.food = self.food.deepCopy()
        state.layout = self.layout.deepCopy()
        state._agentMoved = self._agentMoved
        state._foodEaten = self._foodEaten
        state._foodAdded = self._foodAdded
        state._capsuleEaten = self._capsuleEaten
        return state

    def copyAgentStates(self, agentStates: list['AgentState']) -> list['AgentState']:
        """
        Create copies of all agent states.
        
        Args:
            agentStates: List of AgentState objects to copy
            
        Returns:
            List of copied AgentState objects
        """
        copiedStates = []
        for agentState in agentStates:
            copiedStates.append(agentState.copy())
        return copiedStates

    def __eq__(self, other: 'GameStateData') -> bool:
        """
        Compare this state with another for equality.
        
        Args:
            other: GameStateData to compare against
            
        Returns:
            True if states are equal, False otherwise
        """
        if other == None:
            return False
        # TODO Check for type of other
        if not self.agentStates == other.agentStates:
            return False
        if not self.food == other.food:
            return False
        if not self.capsules == other.capsules:
            return False
        if not self.score == other.score:
            return False
        return True

    def __hash__(self) -> int:
        """Generate hash value for game state."""
        for i, state in enumerate(self.agentStates):
            try:
                int(hash(state))
            except TypeError as e:
                print(e)
                # hash(state)
        return int((hash(tuple(self.agentStates)) + 13*hash(self.food) + 113 * hash(tuple(self.capsules)) + 7 * hash(self.score)) % 1048575)

    def __str__(self) -> str:
        """Generate string representation of game state."""
        width, height = self.layout.width, self.layout.height
        map = Grid(width, height)
        if type(self.food) == type((1, 2)):
            self.food = reconstituteGrid(self.food)
        for x in range(width):
            for y in range(height):
                food, walls = self.food, self.layout.walls
                map[x][y] = self._foodWallStr(food[x][y], walls[x][y])

        for agentState in self.agentStates:
            if agentState == None:
                continue
            if agentState.configuration == None:
                continue
            x, y = [int(i) for i in nearestPoint(agentState.configuration.pos)]
            agent_dir = agentState.configuration.direction
            if agentState.isPacman:
                map[x][y] = self._pacStr(agent_dir)
            else:
                map[x][y] = self._ghostStr(agent_dir)

        for x, y in self.capsules:
            map[x][y] = 'o'

        return f"{str(map)}\nScore: {self.score}\n"

    def _foodWallStr(self, hasFood: bool, hasWall: bool) -> str:
        """
        Get display character for food/wall cell.
        
        Args:
            hasFood: Whether cell contains food
            hasWall: Whether cell contains wall
            
        Returns:
            Character to display for cell
        """
        if hasFood:
            return '.'
        elif hasWall:
            return '%'
        else:
            return ' '

    def _pacStr(self, dir: str) -> str:
        """
        Get display character for Pacman.
        
        Args:
            dir: Direction Pacman is facing
            
        Returns:
            Character representing Pacman
        """
        if dir == Directions.NORTH:
            return 'v'
        if dir == Directions.SOUTH:
            return '^'
        if dir == Directions.WEST:
            return '>'
        return '<'

    def _ghostStr(self, dir: str) -> str:
        """
        Get display character for ghost.
        
        Args:
            dir: Direction ghost is facing
            
        Returns:
            Character representing ghost
        """
        return 'G'
        if dir == Directions.NORTH:
            return 'M'
        if dir == Directions.SOUTH:
            return 'W'
        if dir == Directions.WEST:
            return '3'
        return 'E'

    def initialize(self, layout: 'Layout', numGhostAgents: int) -> None:
        """
        Initialize game state from layout.
        
        Args:
            layout: Layout object containing walls and initial positions
            numGhostAgents: Number of ghost agents in game
        """
        self.food = layout.food.copy()
        #self.capsules = []
        self.capsules = layout.capsules[:]
        self.layout = layout
        self.score = 0
        self.scoreChange = 0

        self.agentStates = []
        numGhosts = 0
        for isPacman, pos in layout.agentPositions:
            if not isPacman:
                if numGhosts == numGhostAgents:
                    continue  # Max ghosts reached already
                else:
                    numGhosts += 1
            self.agentStates.append(AgentState(
                Configuration(pos, Directions.STOP), isPacman))
        self._eaten = [False for a in self.agentStates]


try:
    import boinc
    _BOINC_ENABLED = True
except:
    _BOINC_ENABLED = False

class Game:
    """
    The Game manages the control flow, soliciting actions from agents.
    
    This class handles the main game loop, including:
    - Running each agent's turns in sequence
    - Managing timeouts and crashes
    - Tracking move history and agent timing
    - Updating the display
    - Processing win/loss conditions
    
    Attributes:
        agents: List of agent objects that play the game
        display: The visualization/UI component
        rules: Object defining game rules and constraints
        startingIndex: Index of first agent to move
        muteAgents: Whether to suppress agent output
        catchExceptions: Whether to handle agent exceptions
        moveHistory: List of (agentIndex, action) tuples
        totalAgentTimes: List tracking time used by each agent
        totalAgentTimeWarnings: List tracking timeout warnings per agent
        agentTimeout: Whether any agent has timed out
        agentOutput: List of StringIO buffers for agent output
    """

    def __init__(self, agents: list['Agent'], display: 'Display', rules: 'Rules', 
                 startingIndex: int = 0, muteAgents: bool = False, 
                 catchExceptions: bool = False) -> None:
        self.agentCrashed = False
        self.agents = agents
        self.display = display
        self.rules = rules
        self.startingIndex = startingIndex
        self.gameOver = False
        self.muteAgents = muteAgents
        self.catchExceptions = catchExceptions
        self.moveHistory = []
        self.totalAgentTimes = [0 for agent in agents]
        self.totalAgentTimeWarnings = [0 for agent in agents]
        self.agentTimeout = False
        import io
        self.agentOutput = [io.StringIO() for agent in agents]

    def getProgress(self) -> float:
        """Get game completion progress as a float from 0 to 1."""
        if self.gameOver:
            return 1.0
        else:
            return self.rules.getProgress(self)

    def _agentCrash(self, agentIndex: int, quiet: bool = False) -> None:
        """
        Handle an agent crash.
        
        Args:
            agentIndex: Index of crashed agent
            quiet: Whether to suppress traceback printing
        """
        if not quiet:
            traceback.print_exc()
        self.gameOver = True
        self.agentCrashed = True
        self.rules.agentCrash(self, agentIndex)

    OLD_STDOUT = None
    OLD_STDERR = None

    def mute(self, agentIndex: int) -> None:
        """
        Redirect stdout/stderr to capture agent output.
        
        Args:
            agentIndex: Index of agent to mute
        """
        if not self.muteAgents:
            return
        global OLD_STDOUT, OLD_STDERR
        import io
        OLD_STDOUT = sys.stdout
        OLD_STDERR = sys.stderr
        sys.stdout = self.agentOutput[agentIndex]
        sys.stderr = self.agentOutput[agentIndex]

    def unmute(self) -> None:
        """Restore stdout/stderr to original streams."""
        if not self.muteAgents:
            return
        global OLD_STDOUT, OLD_STDERR
        # Revert stdout/stderr to originals
        sys.stdout = OLD_STDOUT
        sys.stderr = OLD_STDERR

    def run(self) -> None:
        """
        Main control loop for game play.
        
        Handles:
        - Game initialization
        - Agent turns and moves
        - Display updates
        - Win/loss conditions
        - Agent timing and crashes
        - Final cleanup
        """
        self.display.initialize(self.state.data)
        self.numMoves = 0

        # self.display.initialize(self.state.makeObservation(1).data)
        # inform learning agents of the game start
        for i in range(len(self.agents)):
            agent = self.agents[i]
            if not agent:
                self.mute(i)
                # this is a null agent, meaning it failed to load
                # the other team wins
                print(f"Agent {i} failed to load", file=sys.stderr)
                self.unmute()
                self._agentCrash(i, quiet=True)
                return
            if ("registerInitialState" in dir(agent)):
                self.mute(i)
                if self.catchExceptions:
                    try:
                        timed_func = TimeoutFunction(
                            agent.registerInitialState, int(self.rules.getMaxStartupTime(i)))
                        try:
                            start_time = time.time()
                            timed_func(self.state.deepCopy())
                            time_taken = time.time() - start_time
                            self.totalAgentTimes[i] += time_taken
                        except TimeoutFunctionException:
                            print(f"Agent {i} ran out of time on startup!", file=sys.stderr)
                            self.unmute()
                            self.agentTimeout = True
                            self._agentCrash(i, quiet=True)
                            return
                    except Exception as data:
                        self._agentCrash(i, quiet=False)
                        self.unmute()
                        return
                else:
                    agent.registerInitialState(self.state.deepCopy())
                # TODO: could this exceed the total time
                self.unmute()

        agentIndex = self.startingIndex
        numAgents = len(self.agents)

        while not self.gameOver:
            # Fetch the next agent
            agent = self.agents[agentIndex]
            move_time = 0
            skip_action = False
            # Generate an observation of the state
            if 'observationFunction' in dir(agent):
                self.mute(agentIndex)
                if self.catchExceptions:
                    try:
                        timed_func = TimeoutFunction(agent.observationFunction, int(
                            self.rules.getMoveTimeout(agentIndex)))
                        try:
                            start_time = time.time()
                            observation = timed_func(self.state.deepCopy())
                        except TimeoutFunctionException:
                            skip_action = True
                        move_time += time.time() - start_time
                        self.unmute()
                    except Exception as data:
                        self._agentCrash(agentIndex, quiet=False)
                        self.unmute()
                        return
                else:
                    observation = agent.observationFunction(
                        self.state.deepCopy())
                self.unmute()
            else:
                observation = self.state.deepCopy()

            # Solicit an action
            action = None
            self.mute(agentIndex)
            if self.catchExceptions:
                try:
                    timed_func = TimeoutFunction(agent.getAction, int(
                        self.rules.getMoveTimeout(agentIndex)) - int(move_time))
                    try:
                        start_time = time.time()
                        if skip_action:
                            raise TimeoutFunctionException()
                        action = timed_func(observation)
                    except TimeoutFunctionException:
                        print(f"Agent {agentIndex} timed out on a single move!", file=sys.stderr)
                        self.agentTimeout = True
                        self._agentCrash(agentIndex, quiet=True)
                        self.unmute()
                        return

                    move_time += time.time() - start_time

                    if move_time > self.rules.getMoveWarningTime(agentIndex):
                        self.totalAgentTimeWarnings[agentIndex] += 1
                        print(f"Agent {agentIndex} took too long to make a move! This is warning {self.totalAgentTimeWarnings[agentIndex]}", file=sys.stderr)
                        if self.totalAgentTimeWarnings[agentIndex] > self.rules.getMaxTimeWarnings(agentIndex):
                            print(f"Agent {agentIndex} exceeded the maximum number of warnings: {self.totalAgentTimeWarnings[agentIndex]}", file=sys.stderr)
                            self.agentTimeout = True
                            self._agentCrash(agentIndex, quiet=True)
                            self.unmute()
                            return

                    self.totalAgentTimes[agentIndex] += move_time
                    # print "Agent: %d, time: %f, total: %f" % (agentIndex, move_time, self.totalAgentTimes[agentIndex])
                    if self.totalAgentTimes[agentIndex] > self.rules.getMaxTotalTime(agentIndex):
                        print(f"Agent {agentIndex} ran out of time! (time: {self.totalAgentTimes[agentIndex]:.2f})", file=sys.stderr)
                        self.agentTimeout = True
                        self._agentCrash(agentIndex, quiet=True)
                        self.unmute()
                        return
                    self.unmute()
                except Exception as data:
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
            else:
                action = agent.getAction(observation)
            self.unmute()

            # Execute the action
            self.moveHistory.append((agentIndex, action))
            if self.catchExceptions:
                try:
                    self.state = self.state.generateSuccessor(
                        agentIndex, action)
                except Exception as data:
                    self.mute(agentIndex)
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
            else:
                self.state = self.state.generateSuccessor(agentIndex, action)

            # Change the display
            self.display.update(self.state.data)
            ###idx = agentIndex - agentIndex % 2 + 1
            ###self.display.update( self.state.makeObservation(idx).data )

            # Allow for game specific conditions (winning, losing, etc.)
            self.rules.process(self.state, self)
            # Track progress
            if agentIndex == numAgents + 1:
                self.numMoves += 1
            # Next agent
            agentIndex = (agentIndex + 1) % numAgents

            if _BOINC_ENABLED:
                boinc.set_fraction_done(self.getProgress())

        # inform a learning agent of the game result
        for agentIndex, agent in enumerate(self.agents):
            if "final" in dir(agent):
                try:
                    self.mute(agentIndex)
                    agent.final(self.state)
                    self.unmute()
                except Exception as data:
                    if not self.catchExceptions:
                        raise
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
        self.display.finish()
