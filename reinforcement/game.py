"""
Core game mechanics and abstractions for Pacman.

This module provides the fundamental game mechanics and abstractions for the Pacman
game environment. Key components include:

- Agent: Base class for all game agents (Pacman, ghosts)
- GameState: Complete game state representation
- Game: Main game control and rules enforcement
- Directions: Movement constants and utilities
- Configuration: Position and direction tracking
- Grid: 2D grid data structure for game board

The module handles:
- Game rules and mechanics
- State management and transitions  
- Agent movement and interactions
- Score keeping and win conditions
- Game display coordination
- Multi-agent turn management

Most code originally by Dan Klein and John Denero for CS188 at UC Berkeley.
Some code from LiveWires Pacman implementation, used with permission.

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added type hints throughout module
- Added detailed class descriptions
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

from util import *
import time
import os
import traceback
import sys
from typing import List, Tuple, Dict, Optional, Any

#######################
# Parts worth reading #
#######################


class Agent:
    """
    Base class for all agents.

    An agent must define a getAction method that takes a game state and returns an action.
    Optionally, an agent may also implement registerInitialState to inspect the starting state.

    Methods:
        getAction: Returns an action given a game state
        registerInitialState: Optional method to inspect initial state
    """

    def __init__(self, index: int = 0) -> None:
        self.index = index

    def getAction(self, state: 'GameState') -> str:
        """
        Returns an action for the agent to take in the given state.

        Args:
            state: Current game state

        Returns:
            str: Action from Directions.{North, South, East, West, Stop}

        Raises:
            Exception: If not implemented by child class
        """
        raiseNotDefined()


class Directions:
    """Constants and mappings for valid movement directions in the game."""
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
    Stores the (x,y) coordinate and direction of a game entity.

    The coordinate system uses (0,0) as the bottom left corner, with x increasing
    horizontally and y increasing vertically. North corresponds to (0,1).

    Args:
        pos: (x,y) coordinate tuple
        direction: Direction the entity is facing

    Attributes:
        pos: Current position as (x,y) tuple
        direction: Current direction
    """

    def __init__(self, pos: Tuple[float, float], direction: str) -> None:
        self.pos = pos
        self.direction = direction

    def getPosition(self) -> Tuple[float, float]:
        return (self.pos)

    def getDirection(self) -> str:
        return self.direction

    def isInteger(self) -> bool:
        x, y = self.pos
        return x == int(x) and y == int(y)

    def __eq__(self, other: Optional['Configuration']) -> bool:
        if other == None:
            return False
        return (self.pos == other.pos and self.direction == other.direction)

    def __hash__(self) -> int:
        x = hash(self.pos)
        y = hash(self.direction)
        return hash(x + 13 * y)

    def __str__(self) -> str:
        return f"(x,y)={self.pos}, {self.direction}"

    def generateSuccessor(self, vector: Tuple[float, float]) -> 'Configuration':
        """
        Generates a new configuration by moving in the given vector direction.

        Args:
            vector: Movement vector as (dx, dy)

        Returns:
            Configuration: New configuration after moving

        Note: This is a low-level call and does not check if the movement is legal.
        """
        x, y = self.pos
        dx, dy = vector
        direction = Actions.vectorToDirection(vector)
        if direction == Directions.STOP:
            direction = self.direction  # There is no stop direction
        return Configuration((x + dx, y+dy), direction)


class AgentState:
    """
    Stores the complete state of an agent including position, direction and status.

    Args:
        startConfiguration: Initial configuration
        isPacman: Whether this is a Pacman agent

    Attributes:
        start: Starting configuration
        configuration: Current configuration
        isPacman: True if Pacman, False if ghost
        scaredTimer: Time remaining in scared state
        numCarrying: Number of food pellets being carried
        numReturned: Number of food pellets returned
    """

    def __init__(self, startConfiguration: Configuration, isPacman: bool) -> None:
        self.start = startConfiguration
        self.configuration = startConfiguration
        self.isPacman = isPacman
        self.scaredTimer = 0
        # state below potentially used for contest only
        self.numCarrying = 0
        self.numReturned = 0

    def __str__(self) -> str:
        if self.isPacman:
            return f"Pacman: {self.configuration}"
        else:
            return f"Ghost: {self.configuration}"

    def __eq__(self, other: Optional['AgentState']) -> bool:
        if other == None:
            return False
        return self.configuration == other.configuration and self.scaredTimer == other.scaredTimer

    def __hash__(self) -> int:
        return hash(hash(self.configuration) + 13 * hash(self.scaredTimer))

    def copy(self) -> 'AgentState':
        state = AgentState(self.start, self.isPacman)
        state.configuration = self.configuration
        state.scaredTimer = self.scaredTimer
        state.numCarrying = self.numCarrying
        state.numReturned = self.numReturned
        return state

    def getPosition(self) -> Optional[Tuple[float, float]]:
        if self.configuration == None:
            return None
        return self.configuration.getPosition()

    def getDirection(self) -> str:
        return self.configuration.getDirection()


class Grid:
    """
    A 2D grid of boolean values backed by a list of lists.

    The grid uses (x,y) coordinates with (0,0) in the bottom left corner.
    Data is accessed via grid[x][y].

    Args:
        width: Grid width
        height: Grid height
        initialValue: Initial value for all cells
        bitRepresentation: Optional bit-packed representation

    Attributes:
        width: Grid width
        height: Grid height
        data: 2D list storing the grid values
    """

    def __init__(self, width: int, height: int, initialValue: bool = False, bitRepresentation: Optional[Tuple[int, ...]] = None) -> None:
        if initialValue not in [False, True]:
            raise Exception('Grids can only contain booleans')
        self.CELLS_PER_INT = 30

        self.width = width
        self.height = height
        self.data = [[initialValue for y in range(
            height)] for x in range(width)]
        if bitRepresentation:
            self._unpackBits(bitRepresentation)

    def __getitem__(self, i: int) -> List[bool]:
        return self.data[i]

    def __setitem__(self, key: int, item: List[bool]) -> None:
        self.data[key] = item

    def __str__(self) -> str:
        out = [[str(self.data[x][y])[0] for x in range(self.width)]
               for y in range(self.height)]
        out.reverse()
        return '\n'.join([''.join(x) for x in out])

    def __eq__(self, other: Optional['Grid']) -> bool:
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
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deepCopy(self) -> 'Grid':
        return self.copy()

    def shallowCopy(self) -> 'Grid':
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    def count(self, item: bool = True) -> int:
        return sum([x.count(item) for x in self.data])

    def asList(self, key: bool = True) -> List[Tuple[int, int]]:
        list = []
        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] == key:
                    list.append((x, y))
        return list

    def packBits(self) -> Tuple[int, ...]:
        """
        Returns an efficient int list representation of the grid.

        Returns:
            Tuple containing (width, height, bitPackedInts...)
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
        x = index / self.height
        y = index % self.height
        return x, y

    def _unpackBits(self, bits: Tuple[int, ...]) -> None:
        """
        Fills grid data from a bit-packed representation.

        Args:
            bits: Tuple of integers containing packed bits
        """
        cell = 0
        for packed in bits:
            for bit in self._unpackInt(packed, self.CELLS_PER_INT):
                if cell == self.width * self.height:
                    break
                x, y = self._cellIndexToPosition(cell)
                self[x][y] = bit
                cell += 1

    def _unpackInt(self, packed: int, size: int) -> List[bool]:
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


def reconstituteGrid(bitRep: Any) -> Any:
    if type(bitRep) is not type((1, 2)):
        return bitRep
    width, height = bitRep[:2]
    return Grid(width, height, bitRepresentation=bitRep[2:])

####################################
# Parts you shouldn't have to read #
####################################


class Actions:
    """
    Static methods for handling movement actions.
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

    def vectorToDirection(vector: Tuple[float, float]) -> str:
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

    def directionToVector(direction: str, speed: float = 1.0) -> Tuple[float, float]:
        dx, dy = Actions._directions[direction]
        return (dx * speed, dy * speed)
    directionToVector = staticmethod(directionToVector)

    def getPossibleActions(config: Configuration, walls: 'Grid') -> List[str]:
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

    def getLegalNeighbors(position: Tuple[int, int], walls: 'Grid') -> List[Tuple[int, int]]:
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

    def getSuccessor(position: Tuple[float, float], action: str) -> Tuple[float, float]:
        dx, dy = Actions.directionToVector(action)
        x, y = position
        return (x + dx, y + dy)
    getSuccessor = staticmethod(getSuccessor)


class GameStateData:
    """
    Game state data structure containing food, capsules, agent states and score.
    """

    def __init__(self, prevState: Optional['GameStateData'] = None) -> None:
        """
        Generates a new data packet by copying information from its predecessor.

        Args:
            prevState: Previous game state to copy from
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
        state = GameStateData(self)
        state.food = self.food.deepCopy()
        state.layout = self.layout.deepCopy()
        state._agentMoved = self._agentMoved
        state._foodEaten = self._foodEaten
        state._foodAdded = self._foodAdded
        state._capsuleEaten = self._capsuleEaten
        return state

    def copyAgentStates(self, agentStates: List[AgentState]) -> List[AgentState]:
        copiedStates = []
        for agentState in agentStates:
            copiedStates.append(agentState.copy())
        return copiedStates

    def __eq__(self, other: Optional['GameStateData']) -> bool:
        """
        Allows two states to be compared.
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
        """
        Allows states to be keys of dictionaries.
        """
        for i, state in enumerate(self.agentStates):
            try:
                int(hash(state))
            except TypeError as e:
                print(e)
                # hash(state)
        return int((hash(tuple(self.agentStates)) + 13*hash(self.food) + 113 * hash(tuple(self.capsules)) + 7 * hash(self.score)) % 1048575)

    def __str__(self) -> str:
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
        if hasFood:
            return '.'
        elif hasWall:
            return '%'
        else:
            return ' '

    def _pacStr(self, dir: str) -> str:
        if dir == Directions.NORTH:
            return 'v'
        if dir == Directions.SOUTH:
            return '^'
        if dir == Directions.WEST:
            return '>'
        return '<'

    def _ghostStr(self, dir: str) -> str:
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
        Creates an initial game state from a layout array.

        Args:
            layout: Layout object containing walls, food, etc
            numGhostAgents: Number of ghost agents in the game
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
    The Game manages the control flow and state updates, soliciting actions from agents.

    Args:
        agents: List of agent objects that play the game
        display: Display object for visualization
        rules: Rules object defining game logic
        startingIndex: Index of first agent to move
        muteAgents: Whether to suppress agent output
        catchExceptions: Whether to catch agent exceptions

    Attributes:
        agents: List of agents
        display: Display object
        rules: Rules object
        startingIndex: Starting agent index
        gameOver: Whether game has ended
        moveHistory: History of moves made
        totalAgentTimes: Time used by each agent
        agentTimeout: Whether an agent timed out
    """

    def __init__(self, agents: List[Any], display: Any, rules: Any, startingIndex: int = 0, muteAgents: bool = False, catchExceptions: bool = False) -> None:
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
        if self.gameOver:
            return 1.0
        else:
            return self.rules.getProgress(self)

    def _agentCrash(self, agentIndex: int, quiet: bool = False) -> None:
        """Helper method for handling agent crashes"""
        if not quiet:
            traceback.print_exc()
        self.gameOver = True
        self.agentCrashed = True
        self.rules.agentCrash(self, agentIndex)

    OLD_STDOUT = None
    OLD_STDERR = None

    def mute(self, agentIndex: int) -> None:
        if not self.muteAgents:
            return
        global OLD_STDOUT, OLD_STDERR
        import io
        OLD_STDOUT = sys.stdout
        OLD_STDERR = sys.stderr
        sys.stdout = self.agentOutput[agentIndex]
        sys.stderr = self.agentOutput[agentIndex]

    def unmute(self) -> None:
        if not self.muteAgents:
            return
        global OLD_STDOUT, OLD_STDERR
        # Revert stdout/stderr to originals
        sys.stdout = OLD_STDOUT
        sys.stderr = OLD_STDERR

    def run(self) -> None:
        """
        Main control loop for game play.
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
                            print(f"Agent {i} ran out of time on startup!",
                                  file=sys.stderr)
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
                        print(f"Agent {agentIndex} timed out on a single move!",
                              file=sys.stderr)
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
