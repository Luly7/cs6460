"""Game module for Pacman game.

This module provides the core game mechanics and abstractions for the Pacman game,
including agents, game states, rules, and game control flow.

Modified by: George Rudolph at Utah Valley University
Date: 9 Nov 2024

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

import abc
from dataclasses import dataclass, field
from typing import Dict
from util import *
import time, os
import traceback
import sys

#######################
# Parts worth reading #
#######################

class Agent(metaclass=abc.ABCMeta):
    """
    Base class for all game agents.
    
    An agent must define a getAction method to determine its next move.
    It may optionally define additional methods like registerInitialState.

    Attributes:
        index (int): Index identifying this agent in the game
        
    Methods that may be implemented:
        registerInitialState(state): Called at start to inspect initial state
        getAction(state): Required method to determine agent's next action
    """
    def __init__(self, index: int = 0) -> None:
        self.index = index

    @abc.abstractmethod
    def getAction(self, state: 'GameState') -> str:
        """
        Determine the agent's next action based on current game state.

        Args:
            state: Current GameState from pacman, capture, or sonar game
            
        Returns:
            str: Action direction from Directions.{North, South, East, West, Stop}
        """
        return


class Directions:
    """
    Constants and mappings for Pacman movement directions.
    
    Defines the five possible movement directions (NORTH, SOUTH, EAST, WEST, STOP)
    and provides mappings for turning left/right and reversing directions.
    """
    NORTH = 'North'
    SOUTH = 'South'
    EAST = 'East'
    WEST = 'West'
    STOP = 'Stop'

    LEFT = {
        NORTH: WEST,
        SOUTH: EAST,
        EAST: NORTH,
        WEST: SOUTH,
        STOP: STOP
    }

    RIGHT = dict([(y,x) for x, y in LEFT.items()])

    REVERSE = {
        NORTH: SOUTH,
        SOUTH: NORTH,
        EAST: WEST,
        WEST: EAST,
        STOP: STOP
    }
class Configuration:
    """
    A Configuration holds the (x,y) coordinate of a character, along with its
    traveling direction.

    The convention for positions, like a graph, is that (0,0) is the lower left corner, x increases
    horizontally and y increases vertically. Therefore, north is the direction of increasing y, or (0,1).

    Args:
        pos: Tuple of (x,y) coordinates representing position
        direction: String indicating direction of travel (from Directions class)

    Attributes:
        pos: Tuple[float, float] representing (x,y) position
        direction: str indicating direction (North, South, East, West, Stop)
    """

    def __init__(self, pos: Tuple[float, float], direction: str) -> None:
        self.pos = pos
        self.direction = direction

    def getPosition(self) -> Tuple[float, float]:
        """Get the current (x,y) position.
        
        Returns:
            Tuple of (x,y) coordinates
        """
        return (self.pos)

    def getDirection(self) -> str:
        """Get the current direction.
        
        Returns:
            String indicating direction of travel
        """
        return self.direction

    def isInteger(self) -> bool:
        """Check if position coordinates are integers.
        
        Returns:
            True if both x and y coordinates are integers, False otherwise
        """
        x, y = self.pos
        return x == int(x) and y == int(y)

    def __eq__(self, other: Any) -> bool:
        """Check equality with another Configuration.
        
        Args:
            other: Configuration to compare with
            
        Returns:
            True if positions and directions match, False otherwise
        """
        if other == None: return False
        return (self.pos == other.pos and self.direction == other.direction)

    def __hash__(self) -> int:
        """Generate hash value for Configuration.
        
        Returns:
            Integer hash value based on position and direction
        """
        x = hash(self.pos)
        y = hash(self.direction)
        return hash(x + 13 * y)

    def __str__(self) -> str:
        """Get string representation.
        
        Returns:
            String showing position and direction
        """
        return "(x,y)="+str(self.pos)+", "+str(self.direction)

    def generateSuccessor(self, vector: Tuple[float, float]) -> 'Configuration':
        """Generate a new Configuration after applying a movement vector.
        
        Generates a new configuration reached by translating the current
        configuration by the action vector. This is a low-level call and does
        not attempt to respect the legality of the movement.

        Args:
            vector: Tuple of (dx,dy) representing movement vector
            
        Returns:
            New Configuration after applying movement
        """
        x, y = self.pos
        dx, dy = vector
        direction = Actions.vectorToDirection(vector)
        if direction == Directions.STOP:
            direction = self.direction # There is no stop direction
        return Configuration((x + dx, y+dy), direction)

class AgentState:
    """
    AgentStates hold the state of an agent (configuration, speed, scared, etc).
    
    Attributes:
        start (Configuration): Starting configuration of the agent
        configuration (Configuration): Current configuration of the agent 
        isPacman (bool): Whether this agent is Pacman (True) or a ghost (False)
        scaredTimer (int): Number of moves remaining in scared state
        numCarrying (int): Number of food pellets being carried
        numReturned (int): Number of food pellets returned to home
    """

    def __init__(self, startConfiguration: 'Configuration', isPacman: bool) -> None:
        """Initialize agent state.
        
        Args:
            startConfiguration: Initial configuration of the agent
            isPacman: Whether this agent is Pacman (True) or a ghost (False)
        """
        self.start = startConfiguration
        self.configuration = startConfiguration
        self.isPacman = isPacman
        self.scaredTimer = 0
        self.numCarrying = 0
        self.numReturned = 0

    def __str__(self) -> str:
        """Get string representation.
        
        Returns:
            String showing agent type and configuration
        """
        if self.isPacman:
            return "Pacman: " + str(self.configuration)
        else:
            return "Ghost: " + str(self.configuration)

    def __eq__(self, other: Any) -> bool:
        """Check equality with another AgentState.
        
        Args:
            other: AgentState to compare with
            
        Returns:
            True if configurations and scared timers match, False otherwise
        """
        if other == None:
            return False
        return self.configuration == other.configuration and self.scaredTimer == other.scaredTimer

    def __hash__(self) -> int:
        """Generate hash value for AgentState.
        
        Returns:
            Integer hash value based on configuration and scared timer
        """
        return hash(hash(self.configuration) + 13 * hash(self.scaredTimer))

    def copy(self) -> 'AgentState':
        """Create a deep copy of this AgentState.
        
        Returns:
            New AgentState with copied attributes
        """
        state = AgentState(self.start, self.isPacman)
        state.configuration = self.configuration
        state.scaredTimer = self.scaredTimer
        state.numCarrying = self.numCarrying
        state.numReturned = self.numReturned
        return state

    def getPosition(self) -> Optional[Tuple[float, float]]:
        """Get current position of agent.
        
        Returns:
            (x,y) position tuple, or None if no configuration exists
        """
        if self.configuration == None: return None
        return self.configuration.getPosition()

    def getDirection(self) -> str:
        """Get current direction agent is facing.
        
        Returns:
            Direction string ('North', 'South', 'East', 'West', 'Stop')
        """
        return self.configuration.getDirection()

class Grid:
    """
    A 2-dimensional array of objects backed by a list of lists.
    
    Data is accessed via grid[x][y] where (x,y) are positions on a Pacman map with x horizontal,
    y vertical and the origin (0,0) in the bottom left corner.
    
    The __str__ method constructs an output that is oriented like a pacman board.
    
    Args:
        width: Width of the grid in cells
        height: Height of the grid in cells 
        initialValue: Initial boolean value to fill grid with (default False)
        bitRepresentation: Optional bit-packed representation to initialize from
    """
    def __init__(self, width: int, height: int, initialValue: bool = False, 
                 bitRepresentation: Optional[Tuple[int, ...]] = None) -> None:
        if initialValue not in [False, True]: raise Exception('Grids can only contain booleans')
        self.CELLS_PER_INT = 30

        self.width = width
        self.height = height
        self.data = [[initialValue for y in range(height)] for x in range(width)]
        if bitRepresentation:
            self._unpackBits(bitRepresentation)

    def __getitem__(self, i: int) -> List[bool]:
        return self.data[i]

    def __setitem__(self, key: int, item: List[bool]) -> None:
        self.data[key] = item

    def __str__(self) -> str:
        out = [[str(self.data[x][y])[0] for x in range(self.width)] for y in range(self.height)]
        out.reverse()
        return '\n'.join([''.join(x) for x in out])

    def __eq__(self, other: Optional['Grid']) -> bool:
        if other == None: return False
        return self.data == other.data

    def __hash__(self) -> int:
        base = 1
        h = 0
        for l in self.data:
            for i in l:
                if i:
                    h += base
                base *= 2
        return hash(h)

    def copy(self) -> 'Grid':
        """Create a deep copy of this grid.
        
        Returns:
            New Grid with copied data
        """
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deepCopy(self) -> 'Grid':
        """Alias for copy().
        
        Returns:
            Deep copy of this grid
        """
        return self.copy()

    def shallowCopy(self) -> 'Grid':
        """Create a shallow copy sharing the same data.
        
        Returns:
            New Grid referencing the same data
        """
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    def count(self, item: bool = True) -> int:
        """Count cells matching the given value.
        
        Args:
            item: Value to count (default True)
            
        Returns:
            Number of cells matching the value
        """
        return sum([x.count(item) for x in self.data])

    def asList(self, key: bool = True) -> List[Tuple[int, int]]:
        """Return coordinates of cells matching the given value.
        
        Args:
            key: Value to match (default True)
            
        Returns:
            List of (x,y) coordinates where value matches key
        """
        list = []
        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] == key: list.append( (x,y) )
        return list

    def packBits(self) -> Tuple[int, ...]:
        """Pack grid data into an efficient integer representation.
        
        Returns:
            Tuple of (width, height, packed_bits...) where packed_bits
            are integers encoding the boolean grid values
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

    def _cellIndexToPosition(self, index: int) -> Tuple[int, int]:
        """Convert cell index to x,y coordinates.
        
        Args:
            index: Linear index into grid
            
        Returns:
            (x,y) coordinate tuple
        """
        x = index // self.height
        y = index % self.height
        return x, y

    def _unpackBits(self, bits: Tuple[int, ...]) -> None:
        """Fill grid data from bit-level representation.
        
        Args:
            bits: Tuple of integers encoding the grid data
        """
        cell = 0
        for packed in bits:
            for bit in self._unpackInt(packed, self.CELLS_PER_INT):
                if cell == self.width * self.height: break
                x, y = self._cellIndexToPosition(cell)
                self[x][y] = bit
                cell += 1

    def _unpackInt(self, packed: int, size: int) -> List[bool]:
        """Unpack an integer into boolean values.
        
        Args:
            packed: Integer to unpack
            size: Number of boolean values to extract
            
        Returns:
            List of boolean values
            
        Raises:
            ValueError if packed is negative
        """
        bools = []
        if packed < 0: raise ValueError("must be a positive integer")
        for i in range(size):
            n = 2 ** (self.CELLS_PER_INT - i - 1)
            if packed >= n:
                bools.append(True)
                packed -= n
            else:
                bools.append(False)
        return bools

def reconstituteGrid(bitRep: Union[Tuple[int, ...], 'Grid']) -> 'Grid':
    """Reconstruct a Grid from its bit representation.
    
    Args:
        bitRep: Either a Grid object or a tuple of integers encoding a grid
        
    Returns:
        Grid object, either the input Grid or a new one from the bit encoding
    """
    if type(bitRep) is not type((1,2)):
        return bitRep
    width, height = bitRep[:2]
    return Grid(width, height, bitRepresentation= bitRep[2:])

####################################
# Parts you shouldn't have to read #
####################################

class Actions:
    """
    A collection of static methods for manipulating move actions.
    
    Static methods are used in this class because these operations are utility functions
    that don't require access to instance-specific data. They operate purely on their input
    parameters and don't need to maintain any object state.

    For example, reverseDirection() simply maps a direction to its opposite direction,
    and vectorToDirection() converts a movement vector to a cardinal direction. These
    operations are independent of any particular game instance.

    Using static methods provides several benefits:
    1. Clearer intent - Shows these are utility functions that don't depend on instance state
    2. Better organization - Groups related utility functions together in a logical namespace
    3. Memory efficiency - No need to store instance data for these methods
    4. Can be called directly on the class without instantiation
    
    Provides utilities for working with movement actions in the game,
    including direction/vector conversions and legal move calculations.
    """
    # Directions
    _directions: Dict[str, Tuple[int, int]] = {
        Directions.NORTH: (0, 1),
        Directions.SOUTH: (0, -1), 
        Directions.EAST:  (1, 0),
        Directions.WEST:  (-1, 0),
        Directions.STOP:  (0, 0)
    }

    _directionsAsList = _directions.items()

    TOLERANCE: float = .001

    @staticmethod
    def reverseDirection(action: str) -> str:
        """
        Get the opposite direction of an action.
        
        Args:
            action: Direction to reverse ('North', 'South', 'East', 'West')
            
        Returns:
            The opposite direction
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

    @staticmethod
    def vectorToDirection(vector: Tuple[float, float]) -> str:
        """
        Convert a movement vector to a direction.
        
        Args:
            vector: (dx, dy) movement vector
            
        Returns:
            Direction string ('North', 'South', 'East', 'West', or 'Stop')
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

    @staticmethod
    def directionToVector(direction: str, speed: float = 1.0) -> Tuple[float, float]:
        """
        Convert a direction to a movement vector.
        
        Args:
            direction: Direction string ('North', 'South', 'East', 'West', 'Stop')
            speed: Scaling factor for the vector magnitude
            
        Returns:
            (dx, dy) movement vector scaled by speed
        """
        dx, dy = Actions._directions[direction]
        return (dx * speed, dy * speed)

    @staticmethod
    def getPossibleActions(config: 'Configuration', walls: 'Grid') -> List[str]:
        """
        Get the legal actions for an agent in the given configuration.
        
        Args:
            config: Agent's current configuration (position/direction)
            walls: Grid of wall positions
            
        Returns:
            List of legal direction strings the agent can move
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
            if not walls[next_x][next_y]: possible.append(dir)

        return possible

    @staticmethod
    def getLegalNeighbors(position: Tuple[int, int], walls: 'Grid') -> List[Tuple[int, int]]:
        """
        Get legal neighboring positions from the given position.
        
        Args:
            position: (x,y) current position
            walls: Grid of wall positions
            
        Returns:
            List of (x,y) neighboring positions that are not walls
        """
        x,y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []
        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_x = x_int + dx
            if next_x < 0 or next_x == walls.width: continue
            next_y = y_int + dy
            if next_y < 0 or next_y == walls.height: continue
            if not walls[next_x][next_y]: neighbors.append((next_x, next_y))
        return neighbors

    @staticmethod
    def getSuccessor(position: Tuple[float, float], action: str) -> Tuple[float, float]:
        """
        Get the next position after taking an action.
        
        Args:
            position: (x,y) current position
            action: Direction to move ('North', 'South', 'East', 'West', 'Stop')
            
        Returns:
            (x,y) next position after taking the action
        """
        dx, dy = Actions.directionToVector(action)
        x, y = position
        return (x + dx, y + dy)

class GameStateData:
    """
    A class that stores the complete game state data.
    
    Includes food locations, capsule locations, agent states, score,
    and various flags tracking game events.
    """
    def __init__(self, prevState: Optional['GameStateData'] = None) -> None:
        """
        Initialize game state data, optionally copying from previous state.
        
        Args:
            prevState: Previous game state to copy from, if any
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
        """
        Create a deep copy of the game state.
        
        Returns:
            A new GameStateData instance with deep copies of all fields
        """
        state = GameStateData(self)
        state.food = self.food.deepCopy()
        state.layout = self.layout.deepCopy()
        state._agentMoved = self._agentMoved
        state._foodEaten = self._foodEaten
        state._foodAdded = self._foodAdded
        state._capsuleEaten = self._capsuleEaten
        return state

    def copyAgentStates(self, agentStates: List['AgentState']) -> List['AgentState']:
        """
        Create copies of all agent states.
        
        Args:
            agentStates: List of agent states to copy
            
        Returns:
            List of copied agent states
        """
        copiedStates = []
        for agentState in agentStates:
            copiedStates.append(agentState.copy())
        return copiedStates

    def __eq__(self, other: Optional['GameStateData']) -> bool:
        """
        Compare this state with another for equality.
        
        Args:
            other: GameStateData instance to compare against
            
        Returns:
            True if states are equal, False otherwise
        """
        if other == None: return False
        if not self.agentStates == other.agentStates: return False
        if not self.food == other.food: return False
        if not self.capsules == other.capsules: return False
        if not self.score == other.score: return False
        return True

    def __hash__(self) -> int:
        """
        Generate a hash value for this game state.
        
        Returns:
            Integer hash value
        """
        for i, state in enumerate(self.agentStates):
            try:
                int(hash(state))
            except TypeError as e:
                print(e)
        return int((hash(tuple(self.agentStates)) + 13*hash(self.food) + 113* hash(tuple(self.capsules)) + 7 * hash(self.score)) % 1048575)

    def __str__(self) -> str:
        """
        Create string representation of game state.
        
        Returns:
            Multi-line string showing game board and score
        """
        width, height = self.layout.width, self.layout.height
        map = Grid(width, height)
        if type(self.food) == type((1,2)):
            self.food = reconstituteGrid(self.food)
        for x in range(width):
            for y in range(height):
                food, walls = self.food, self.layout.walls
                map[x][y] = self._foodWallStr(food[x][y], walls[x][y])

        for agentState in self.agentStates:
            if agentState == None: continue
            if agentState.configuration == None: continue
            x,y = [int(i) for i in nearestPoint(agentState.configuration.pos)]
            agent_dir = agentState.configuration.direction
            if agentState.isPacman:
                map[x][y] = self._pacStr(agent_dir)
            else:
                map[x][y] = self._ghostStr(agent_dir)

        for x, y in self.capsules:
            map[x][y] = 'o'

        return str(map) + ("\nScore: %d\n" % self.score)

    def _foodWallStr(self, hasFood: bool, hasWall: bool) -> str:
        """
        Get character representation for food/wall cell.
        
        Args:
            hasFood: Whether cell contains food
            hasWall: Whether cell contains wall
            
        Returns:
            Character representing cell contents
        """
        if hasFood:
            return '.'
        elif hasWall:
            return '%'
        else:
            return ' '

    def _pacStr(self, dir: str) -> str:
        """
        Get character representation for Pacman.
        
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
        Get character representation for ghost.
        
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
            layout: Layout object containing initial game configuration
            numGhostAgents: Number of ghost agents in game
        """
        self.food = layout.food.copy()
        self.capsules = layout.capsules[:]
        self.layout = layout
        self.score = 0
        self.scoreChange = 0

        self.agentStates = []
        numGhosts = 0
        for isPacman, pos in layout.agentPositions:
            if not isPacman:
                if numGhosts == numGhostAgents: continue
                else: numGhosts += 1
            self.agentStates.append(AgentState(Configuration(pos, Directions.STOP), isPacman))
        self._eaten = [False for a in self.agentStates]

# BOINC (Berkeley Open Infrastructure for Network Computing) is a platform 
# for volunteer and grid computing. It allows users to donate their computer's
# spare processing power to scientific research projects.
try:
    import boinc  # Import BOINC client library if available
    _BOINC_ENABLED = True
except:
    _BOINC_ENABLED = False  # Disable BOINC integration if not installed

class Game:
    """
    The Game manages the control flow, soliciting actions from agents.
    
    Handles the main game loop, agent interactions, timing, crashes, and display updates.
    
    Args:
        agents: List of agent objects that play the game
        display: The graphics display object
        rules: Rules object defining game logic
        startingIndex: Index of first agent to move (default 0)
        muteAgents: Whether to suppress agent output (default False)
        catchExceptions: Whether to catch agent exceptions (default False)
    """

    def __init__(self, agents: List[Any], display: Any, rules: Any, 
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
        self.moveHistory: List[Tuple[int, str]] = []
        self.totalAgentTimes = [0 for agent in agents]
        self.totalAgentTimeWarnings = [0 for agent in agents]
        self.agentTimeout = False
        import io
        self.agentOutput = [io.StringIO() for agent in agents]

    def getProgress(self) -> float:
        """
        Get the progress of the game between 0 and 1.
        
        Returns:
            Float between 0 and 1 indicating game progress
        """
        if self.gameOver:
            return 1.0
        else:
            return self.rules.getProgress(self)

    def _agentCrash(self, agentIndex: int, quiet: bool = False) -> None:
        """
        Helper method for handling agent crashes.
        
        Args:
            agentIndex: Index of crashed agent
            quiet: Whether to suppress traceback output
        """
        if not quiet: traceback.print_exc()
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
        if not self.muteAgents: return
        global OLD_STDOUT, OLD_STDERR
        import io
        OLD_STDOUT = sys.stdout
        OLD_STDERR = sys.stderr
        sys.stdout = self.agentOutput[agentIndex]
        sys.stderr = self.agentOutput[agentIndex]

    def unmute(self) -> None:
        """Restore stdout/stderr to originals."""
        if not self.muteAgents: return
        global OLD_STDOUT, OLD_STDERR
        # Revert stdout/stderr to originals
        sys.stdout = OLD_STDOUT
        sys.stderr = OLD_STDERR

    def run(self) -> None:
        """
        Main control loop for game play.
        
        Handles:
        - Initializing agents and display
        - Main game loop getting actions from agents
        - Timing agent moves and handling timeouts
        - Updating game state and display
        - Processing win/loss conditions
        - Cleanup and final agent notifications
        """
        self.display.initialize(self.state.data)
        self.numMoves = 0

        ###self.display.initialize(self.state.makeObservation(1).data)
        # inform learning agents of the game start
        for i in range(len(self.agents)):
            agent = self.agents[i]
            if not agent:
                self.mute(i)
                # this is a null agent, meaning it failed to load
                # the other team wins
                print("Agent %d failed to load" % i, file=sys.stderr)
                self.unmute()
                self._agentCrash(i, quiet=True)
                return
            if ("registerInitialState" in dir(agent)):
                self.mute(i)
                if self.catchExceptions:
                    try:
                        timed_func = TimeoutFunction(agent.registerInitialState, int(self.rules.getMaxStartupTime(i)))
                        try:
                            start_time = time.time()
                            timed_func(self.state.deepCopy())
                            time_taken = time.time() - start_time
                            self.totalAgentTimes[i] += time_taken
                        except TimeoutFunctionException:
                            print("Agent %d ran out of time on startup!" % i, file=sys.stderr)
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
                ## TODO: could this exceed the total time
                self.unmute()

        agentIndex = self.startingIndex
        numAgents = len( self.agents )

        while not self.gameOver:
            # Fetch the next agent
            agent = self.agents[agentIndex]
            move_time = 0
            skip_action = False
            # Generate an observation of the state
            if 'observationFunction' in dir( agent ):
                self.mute(agentIndex)
                if self.catchExceptions:
                    try:
                        timed_func = TimeoutFunction(agent.observationFunction, int(self.rules.getMoveTimeout(agentIndex)))
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
                    observation = agent.observationFunction(self.state.deepCopy())
                self.unmute()
            else:
                observation = self.state.deepCopy()

            # Solicit an action
            action = None
            self.mute(agentIndex)
            if self.catchExceptions:
                try:
                    timed_func = TimeoutFunction(agent.getAction, int(self.rules.getMoveTimeout(agentIndex)) - int(move_time))
                    try:
                        start_time = time.time()
                        if skip_action:
                            raise TimeoutFunctionException()
                        action = timed_func( observation )
                    except TimeoutFunctionException:
                        print("Agent %d timed out on a single move!" % agentIndex, file=sys.stderr)
                        self.agentTimeout = True
                        self._agentCrash(agentIndex, quiet=True)
                        self.unmute()
                        return

                    move_time += time.time() - start_time

                    if move_time > self.rules.getMoveWarningTime(agentIndex):
                        self.totalAgentTimeWarnings[agentIndex] += 1
                        print("Agent %d took too long to make a move! This is warning %d" % (agentIndex, self.totalAgentTimeWarnings[agentIndex]), file=sys.stderr)
                        if self.totalAgentTimeWarnings[agentIndex] > self.rules.getMaxTimeWarnings(agentIndex):
                            print("Agent %d exceeded the maximum number of warnings: %d" % (agentIndex, self.totalAgentTimeWarnings[agentIndex]), file=sys.stderr)
                            self.agentTimeout = True
                            self._agentCrash(agentIndex, quiet=True)
                            self.unmute()
                            return

                    self.totalAgentTimes[agentIndex] += move_time
                    #print("Agent: %d, time: %f, total: %f" % (agentIndex, move_time, self.totalAgentTimes[agentIndex]))
                    if self.totalAgentTimes[agentIndex] > self.rules.getMaxTotalTime(agentIndex):
                        print("Agent %d ran out of time! (time: %1.2f)" % (agentIndex, self.totalAgentTimes[agentIndex]), file=sys.stderr)
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
            self.moveHistory.append( (agentIndex, action) )
            if self.catchExceptions:
                try:
                    self.state = self.state.generateSuccessor( agentIndex, action )
                except Exception as data:
                    self.mute(agentIndex)
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
            else:
                self.state = self.state.generateSuccessor( agentIndex, action )

            # Change the display
            self.display.update( self.state.data )
            ###idx = agentIndex - agentIndex % 2 + 1
            ###self.display.update( self.state.makeObservation(idx).data )

            # Allow for game specific conditions (winning, losing, etc.)
            self.rules.process(self.state, self)
            # Track progress
            if agentIndex == numAgents + 1: self.numMoves += 1
            # Next agent
            agentIndex = ( agentIndex + 1 ) % numAgents

            if _BOINC_ENABLED:
                boinc.set_fraction_done(self.getProgress())

        # inform a learning agent of the game result
        for agentIndex, agent in enumerate(self.agents):
            if "final" in dir( agent ) :
                try:
                    self.mute(agentIndex)
                    agent.final( self.state )
                    self.unmute()
                except Exception as data:
                    if not self.catchExceptions: raise data
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
        self.display.finish()
