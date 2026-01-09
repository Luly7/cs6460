"""Core game logic and mechanics for the classic Pacman game.

This module implements the main game engine and mechanics for Pacman, including game state
management, movement rules, collision detection, and scoring. It is organized into three
main sections:

1. Pacman World Interface:
   Core classes and methods for interacting with the game environment, including the
   GameState class that tracks the full game state. This section contains the essential
   code needed for implementing Pacman agents.

2. Game Mechanics:
   Internal logic that governs game rules, movement validation, collision handling,
   and other core game behaviors. This section manages the underlying game mechanics
   but generally doesn't need to be modified.

3. Game Framework:
   Setup and initialization code for starting new games, processing command line options,
   and connecting the various game components (agents, graphics, etc). This section
   handles the game's execution flow.

To play the game manually:
    python pacman.py
Use WASD or arrow keys to move Pacman.

Originally developed at UC Berkeley for CS188 Intro to AI.
Modified by George Rudolph on 12 Nov 2024:
- Added type hints throughout the codebase
- Improved documentation and docstrings
- Verified compatibility with Python 3.13

Original Licensing Information:  
You are free to use or extend these projects for educational purposes provided that
(1) you do not distribute or publish solutions
(2) you retain this notice
(3) you provide clear attribution to UC Berkeley, including a link to http://ai.berkeley.edu

Original Attribution:
The Pacman AI projects were developed at UC Berkeley.
Core projects and autograders created by John DeNero (denero@cs.berkeley.edu) 
and Dan Klein (klein@cs.berkeley.edu).
Student side autograding added by Brad Miller, Nick Hay, and Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""
from game import GameStateData
from game import Game
from game import Directions
from game import Actions
from util import nearestPoint
from util import manhattanDistance
import util
import layout
import sys
import types
import time
import random
import os
from typing import List, Set, Optional, Tuple, Any, Dict

###################################################
# YOUR INTERFACE TO THE PACMAN WORLD: A GameState #
###################################################


class GameState:
    """
    A GameState specifies the full game state, including the food, capsules,
    agent configurations and score changes.

    GameStates are used by the Game object to capture the actual state of the game and
    can be used by agents to reason about the game.

    Much of the information in a GameState is stored in a GameStateData object.  We
    strongly suggest that you access that data via the accessor methods below rather
    than referring to the GameStateData object directly.

    Note that in classic Pacman, Pacman is always agent 0.

    Attributes:
        explored (Set[GameState]): Static set tracking which states have had getLegalActions called
        data (GameStateData): The underlying game state data
    """

    # Static variable keeps track of which states have had getLegalActions called
    explored: Set['GameState'] = set()

    @staticmethod
    def getAndResetExplored() -> Set['GameState']:
        """Get and clear the set of explored states.
        
        Returns:
            Set of GameState objects that have been explored
        """
        tmp = GameState.explored.copy()
        GameState.explored = set()
        return tmp

    def getLegalActions(self, agentIndex: int = 0) -> List[str]:
        """Get the legal actions for the specified agent.
        
        Args:
            agentIndex: Index of the agent (0 for Pacman, >0 for ghosts)
            
        Returns:
            List of legal action strings for the agent
        """
        if self.isWin() or self.isLose():
            return []

        if agentIndex == 0:  # Pacman is moving
            return PacmanRules.getLegalActions(self)
        else:
            return GhostRules.getLegalActions(self, agentIndex)

    def generateSuccessor(self, agentIndex: int, action: str) -> 'GameState':
        """Generate the successor state after an agent takes an action.
        
        Args:
            agentIndex: Index of the agent taking the action
            action: The action being taken
            
        Returns:
            The successor GameState
            
        Raises:
            Exception: If trying to generate successor of a terminal state
        """
        # Check that successors exist
        if self.isWin() or self.isLose():
            raise Exception('Can\'t generate a successor of a terminal state.')

        # Copy current state
        state = GameState(self)

        # Let agent's logic deal with its action's effects on the board
        if agentIndex == 0:  # Pacman is moving
            state.data._eaten = [False for i in range(state.getNumAgents())]
            PacmanRules.applyAction(state, action)
        else:                # A ghost is moving
            GhostRules.applyAction(state, action, agentIndex)

        # Time passes
        if agentIndex == 0:
            state.data.scoreChange += -TIME_PENALTY  # Penalty for waiting around
        else:
            GhostRules.decrementTimer(state.data.agentStates[agentIndex])

        # Resolve multi-agent effects
        GhostRules.checkDeath(state, agentIndex)

        # Book keeping
        state.data._agentMoved = agentIndex
        state.data.score += state.data.scoreChange
        GameState.explored.add(self)
        GameState.explored.add(state)
        return state

    def getLegalPacmanActions(self) -> List[str]:
        """Get legal actions for Pacman (agent 0).
        
        Returns:
            List of legal action strings for Pacman
        """
        return self.getLegalActions(0)

    def generatePacmanSuccessor(self, action: str) -> 'GameState':
        """Generate successor state after Pacman takes an action.
        
        Args:
            action: The action being taken by Pacman
            
        Returns:
            The successor GameState
        """
        return self.generateSuccessor(0, action)

    def getPacmanState(self) -> Any:
        """Get Pacman's agent state.
        
        Returns:
            AgentState object containing Pacman's position and direction
        """
        return self.data.agentStates[0].copy()

    def getPacmanPosition(self) -> Tuple[int, int]:
        """Get Pacman's current position.
        
        Returns:
            (x,y) tuple of Pacman's position
        """
        return self.data.agentStates[0].getPosition()

    def getGhostStates(self) -> List[Any]:
        """Get states of all ghosts.
        
        Returns:
            List of ghost AgentState objects
        """
        return self.data.agentStates[1:]

    def getGhostState(self, agentIndex: int) -> Any:
        """Get state of a specific ghost.
        
        Args:
            agentIndex: Index of the ghost agent
            
        Returns:
            AgentState object for the specified ghost
            
        Raises:
            Exception: If invalid agent index provided
        """
        if agentIndex == 0 or agentIndex >= self.getNumAgents():
            raise Exception("Invalid index passed to getGhostState")
        return self.data.agentStates[agentIndex]

    def getGhostPosition(self, agentIndex: int) -> Tuple[int, int]:
        """Get position of a specific ghost.
        
        Args:
            agentIndex: Index of the ghost agent
            
        Returns:
            (x,y) tuple of ghost's position
            
        Raises:
            Exception: If Pacman's index (0) is provided
        """
        if agentIndex == 0:
            raise Exception("Pacman's index passed to getGhostPosition")
        return self.data.agentStates[agentIndex].getPosition()

    def getGhostPositions(self) -> List[Tuple[int, int]]:
        """Get positions of all ghosts.
        
        Returns:
            List of (x,y) position tuples for all ghosts
        """
        return [s.getPosition() for s in self.getGhostStates()]

    def getNumAgents(self) -> int:
        """Get total number of agents (Pacman + ghosts).
        
        Returns:
            Number of agents in the game
        """
        return len(self.data.agentStates)

    def getScore(self) -> float:
        """Get current game score.
        
        Returns:
            Current score as a float
        """
        return float(self.data.score)

    def getCapsules(self) -> List[Tuple[int, int]]:
        """Get positions of remaining power capsules.
        
        Returns:
            List of (x,y) capsule positions
        """
        return self.data.capsules

    def getNumFood(self) -> int:
        """Get count of remaining food pellets.
        
        Returns:
            Number of food pellets remaining
        """
        return self.data.food.count()

    def getFood(self) -> Any:
        """Get grid of food locations.
        
        Returns:
            Grid of boolean food indicators
        """
        return self.data.food

    def getWalls(self) -> Any:
        """Get grid of wall locations.
        
        Returns:
            Grid of boolean wall indicators
        """
        return self.data.layout.walls

    def hasFood(self, x: int, y: int) -> bool:
        """Check if there is food at a location.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            True if food exists at (x,y), False otherwise
        """
        return self.data.food[x][y]

    def hasWall(self, x: int, y: int) -> bool:
        """Check if there is a wall at a location.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            True if wall exists at (x,y), False otherwise
        """
        return self.data.layout.walls[x][y]

    def isLose(self) -> bool:
        """Check if this is a losing state.
        
        Returns:
            True if game is lost, False otherwise
        """
        return self.data._lose

    def isWin(self) -> bool:
        """Check if this is a winning state.
        
        Returns:
            True if game is won, False otherwise
        """
        return self.data._win

    #############################################
    #             Helper methods:               #
    # You shouldn't need to call these directly #
    #############################################

    def __init__(self, prevState=None):
        """
        Generates a new state by copying information from its predecessor.
        """
        if prevState != None:  # Initial state
            self.data = GameStateData(prevState.data)
        else:
            self.data = GameStateData()

    def deepCopy(self):
        state = GameState(self)
        state.data = self.data.deepCopy()
        return state

    def __eq__(self, other):
        """
        Allows two states to be compared.
        """
        return hasattr(other, 'data') and self.data == other.data

    def __hash__(self):
        """
        Allows states to be keys of dictionaries.
        """
        return hash(self.data)

    def __str__(self):

        return str(self.data)

    def initialize(self, layout, numGhostAgents=1000):
        """
        Creates an initial game state from a layout array (see layout.py).
        """
        self.data.initialize(layout, numGhostAgents)

############################################################################
#                     THE HIDDEN SECRETS OF PACMAN                         #
#                                                                          #
# You shouldn't need to look through the code in this section of the file. #
############################################################################


SCARED_TIME: int = 40    # Moves ghosts are scared
COLLISION_TOLERANCE: float = 0.7  # How close ghosts must be to Pacman to kill
TIME_PENALTY: int = 1  # Number of points lost each round


class ClassicGameRules:
    """These game rules manage the control flow of a game.
    
    This class handles the game lifecycle, including starting new games,
    processing game state changes, and handling win/loss conditions.
    
    Attributes:
        timeout: Maximum time allowed for agent moves in seconds
        initialState: Deep copy of the initial game state
        quiet: Whether to suppress output messages
    """

    def __init__(self, timeout: int = 30) -> None:
        """Initialize game rules with a timeout value.
        
        Args:
            timeout: Maximum time in seconds allowed for agent moves
        """
        self.timeout = timeout

    def newGame(self, layout, pacmanAgent, ghostAgents, display, quiet: bool = False, catchExceptions: bool = False) -> Game:
        """Create and initialize a new game instance.
        
        Args:
            layout: The game board layout
            pacmanAgent: The Pacman agent instance
            ghostAgents: List of ghost agent instances
            display: The game display interface
            quiet: Whether to suppress output messages
            catchExceptions: Whether to catch and handle agent exceptions
            
        Returns:
            A new Game instance ready to start
        """
        agents = [pacmanAgent] + ghostAgents[:layout.getNumGhosts()]
        initState = GameState()
        initState.initialize(layout, len(ghostAgents))
        game = Game(agents, display, self, catchExceptions=catchExceptions)
        game.state = initState
        self.initialState = initState.deepCopy()
        self.quiet = quiet
        return game

    def process(self, state: GameState, game: Game) -> None:
        """Check if the game should end based on win/loss conditions.
        
        Args:
            state: Current game state
            game: Current game instance
        """
        if state.isWin():
            self.win(state, game)
        if state.isLose():
            self.lose(state, game)

    def win(self, state: GameState, game: Game) -> None:
        """Handle game win condition.
        
        Args:
            state: Final game state
            game: Current game instance
        """
        if not self.quiet:
            print(f"Pacman emerges victorious! Score: {state.data.score}")
        game.gameOver = True

    def lose(self, state: GameState, game: Game) -> None:
        """Handle game loss condition.
        
        Args:
            state: Final game state
            game: Current game instance
        """
        if not self.quiet:
            print(f"Pacman died! Score: {state.data.score}")
        game.gameOver = True

    def getProgress(self, game: Game) -> float:
        """Calculate game progress as ratio of remaining food.
        
        Args:
            game: Current game instance
            
        Returns:
            Progress ratio between 0 and 1
        """
        return float(game.state.getNumFood()) / self.initialState.getNumFood()

    def agentCrash(self, game: Game, agentIndex: int) -> None:
        """Handle agent crashes during gameplay.
        
        Args:
            game: Current game instance
            agentIndex: Index of crashed agent (0 for Pacman)
        """
        if agentIndex == 0:
            print("Pacman crashed")
        else:
            print("A ghost crashed")

    def getMaxTotalTime(self, agentIndex: int) -> int:
        """Get maximum total time allowed for an agent.
        
        Args:
            agentIndex: Index of the agent
            
        Returns:
            Time limit in seconds
        """
        return self.timeout

    def getMaxStartupTime(self, agentIndex: int) -> int:
        """Get maximum startup time allowed for an agent.
        
        Args:
            agentIndex: Index of the agent
            
        Returns:
            Time limit in seconds
        """
        return self.timeout

    def getMoveWarningTime(self, agentIndex: int) -> int:
        """Get warning time threshold for agent moves.
        
        Args:
            agentIndex: Index of the agent
            
        Returns:
            Warning time threshold in seconds
        """
        return self.timeout

    def getMoveTimeout(self, agentIndex: int) -> int:
        """Get timeout limit for individual agent moves.
        
        Args:
            agentIndex: Index of the agent
            
        Returns:
            Move timeout in seconds
        """
        return self.timeout

    def getMaxTimeWarnings(self, agentIndex: int) -> int:
        """Get maximum number of time warnings allowed.
        
        Args:
            agentIndex: Index of the agent
            
        Returns:
            Maximum number of warnings
        """
        return 0

class PacmanRules:
    """
    These functions govern how pacman interacts with his environment under
    the classic game rules.
    """
    PACMAN_SPEED = 1

    def getLegalActions(state):
        """
        Returns a list of possible actions.
        """
        return Actions.getPossibleActions(state.getPacmanState().configuration, state.data.layout.walls)
    getLegalActions = staticmethod(getLegalActions)

    def applyAction(state, action):
        """
        Edits the state to reflect the results of the action.
        """
        legal = PacmanRules.getLegalActions(state)
        if action not in legal:
            raise Exception("Illegal action " + str(action))

        pacmanState = state.data.agentStates[0]

        # Update Configuration
        vector = Actions.directionToVector(action, PacmanRules.PACMAN_SPEED)
        pacmanState.configuration = pacmanState.configuration.generateSuccessor(
            vector)

        # Eat
        next = pacmanState.configuration.getPosition()
        nearest = nearestPoint(next)
        if manhattanDistance(nearest, next) <= 0.5:
            # Remove food
            PacmanRules.consume(nearest, state)
    applyAction = staticmethod(applyAction)

    def consume(position, state):
        x, y = position
        # Eat food
        if state.data.food[x][y]:
            state.data.scoreChange += 10
            state.data.food = state.data.food.copy()
            state.data.food[x][y] = False
            state.data._foodEaten = position
            # TODO: cache numFood?
            numFood = state.getNumFood()
            if numFood == 0 and not state.data._lose:
                state.data.scoreChange += 500
                state.data._win = True
        # Eat capsule
        if(position in state.getCapsules()):
            state.data.capsules.remove(position)
            state.data._capsuleEaten = position
            # Reset all ghosts' scared timers
            for index in range(1, len(state.data.agentStates)):
                state.data.agentStates[index].scaredTimer = SCARED_TIME
    consume = staticmethod(consume)


class GhostRules:
    """These functions dictate how ghosts interact with their environment.
    
    This class contains static methods that handle ghost movement rules, legal actions,
    collisions with Pacman, and other ghost-specific game mechanics.
    
    Attributes:
        GHOST_SPEED (float): Base movement speed for ghosts
    """
    GHOST_SPEED: float = 1.0

    def getLegalActions(state: GameState, ghostIndex: int) -> List[str]:
        """Get the legal actions for a ghost at the given index.
        
        Ghosts cannot stop, and cannot turn around unless they reach a dead end,
        but can turn 90 degrees at intersections.
        
        Args:
            state: Current game state
            ghostIndex: Index of the ghost to get actions for
            
        Returns:
            List of legal direction actions the ghost can take
        """
        conf = state.getGhostState(ghostIndex).configuration
        possibleActions = Actions.getPossibleActions(
            conf, state.data.layout.walls)
        reverse = Actions.reverseDirection(conf.direction)
        if Directions.STOP in possibleActions:
            possibleActions.remove(Directions.STOP)
        if reverse in possibleActions and len(possibleActions) > 1:
            possibleActions.remove(reverse)
        return possibleActions
    getLegalActions = staticmethod(getLegalActions)

    def applyAction(state: GameState, action: str, ghostIndex: int) -> None:
        """Apply the given action to move a ghost in the game state.
        
        Args:
            state: Current game state
            action: Direction action to apply
            ghostIndex: Index of the ghost to move
            
        Raises:
            Exception: If the action is not legal for the ghost
        """
        legal = GhostRules.getLegalActions(state, ghostIndex)
        if action not in legal:
            raise Exception(f"Illegal ghost action {action}")

        ghostState = state.data.agentStates[ghostIndex]
        speed = GhostRules.GHOST_SPEED
        if ghostState.scaredTimer > 0:
            speed /= 2.0
        vector = Actions.directionToVector(action, speed)
        ghostState.configuration = ghostState.configuration.generateSuccessor(
            vector)
    applyAction = staticmethod(applyAction)

    def decrementTimer(ghostState) -> None:
        """Decrease the scared timer for a ghost.
        
        Args:
            ghostState: The ghost state to update
        """
        timer = ghostState.scaredTimer
        if timer == 1:
            ghostState.configuration.pos = nearestPoint(
                ghostState.configuration.pos)
        ghostState.scaredTimer = max(0, timer - 1)
    decrementTimer = staticmethod(decrementTimer)

    def checkDeath(state: GameState, agentIndex: int) -> None:
        """Check if Pacman and ghost collisions result in death.
        
        Args:
            state: Current game state
            agentIndex: Index of agent that just moved
        """
        pacmanPosition = state.getPacmanPosition()
        if agentIndex == 0:  # Pacman just moved; Anyone can kill him
            for index in range(1, len(state.data.agentStates)):
                ghostState = state.data.agentStates[index]
                ghostPosition = ghostState.configuration.getPosition()
                if GhostRules.canKill(pacmanPosition, ghostPosition):
                    GhostRules.collide(state, ghostState, index)
        else:
            ghostState = state.data.agentStates[agentIndex]
            ghostPosition = ghostState.configuration.getPosition()
            if GhostRules.canKill(pacmanPosition, ghostPosition):
                GhostRules.collide(state, ghostState, agentIndex)
    checkDeath = staticmethod(checkDeath)

    def collide(state: GameState, ghostState, agentIndex: int) -> None:
        """Handle collision between Pacman and a ghost.
        
        Args:
            state: Current game state
            ghostState: State of the ghost involved in collision
            agentIndex: Index of the ghost agent
        """
        if ghostState.scaredTimer > 0:
            state.data.scoreChange += 200
            GhostRules.placeGhost(state, ghostState)
            ghostState.scaredTimer = 0
            # Added for first-person
            state.data._eaten[agentIndex] = True
        else:
            if not state.data._win:
                state.data.scoreChange -= 500
                state.data._lose = True
    collide = staticmethod(collide)

    def canKill(pacmanPosition: Tuple[float, float], ghostPosition: Tuple[float, float]) -> bool:
        """Check if a ghost can kill Pacman at the given positions.
        
        Args:
            pacmanPosition: (x,y) position of Pacman
            ghostPosition: (x,y) position of ghost
            
        Returns:
            True if ghost can kill Pacman, False otherwise
        """
        return manhattanDistance(ghostPosition, pacmanPosition) <= COLLISION_TOLERANCE
    canKill = staticmethod(canKill)

    def placeGhost(state: GameState, ghostState) -> None:
        """Place a ghost back at its starting position.
        
        Args:
            state: Current game state
            ghostState: The ghost state to reset
        """
        ghostState.configuration = ghostState.start
    placeGhost = staticmethod(placeGhost)


#############################
# FRAMEWORK TO START A GAME #
#############################


def default(str: str) -> str:
    """Add default value notation to option string.
    
    Args:
        str: The option string to modify
        
    Returns:
        String with default value notation appended
    """
    return f'{str} [Default: %default]'


def parseAgentArgs(str: Optional[str]) -> Dict[str, Any]:
    """Parse comma-separated agent arguments into a dictionary.
    
    Args:
        str: Comma-separated string of key=value pairs
        
    Returns:
        Dictionary mapping argument names to values
    """
    if str == None:
        return {}
    pieces = str.split(',')
    opts = {}
    for p in pieces:
        if '=' in p:
            key, val = p.split('=')
        else:
            key, val = p, 1
        opts[key] = val
    return opts


def readCommand(argv: List[str]) -> Dict[str, Any]:
    """Process command line arguments for running Pacman.
    
    Parses command line arguments and returns a dictionary of game settings
    including layout, agents, display options, etc.
    
    Args:
        argv: List of command line argument strings
        
    Returns:
        Dictionary containing all game configuration options
        
    Raises:
        Exception: If command line arguments cannot be parsed
    """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python pacman.py <options>
    EXAMPLES:   (1) python pacman.py
                    - starts an interactive game
                (2) python pacman.py --layout smallClassic --zoom 2
                OR  python pacman.py -l smallClassic -z 2
                    - starts an interactive game on a smaller board, zoomed in
    """
    parser = OptionParser(usageStr)

    parser.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    parser.add_option('-l', '--layout', dest='layout',
                      help=default('the LAYOUT_FILE from which to load the map layout'),
                      metavar='LAYOUT_FILE', default='mediumClassic')
    parser.add_option('-p', '--pacman', dest='pacman',
                      help=default('the agent TYPE in the pacmanAgents module to use'),
                      metavar='TYPE', default='KeyboardAgent')
    parser.add_option('-t', '--textGraphics', action='store_true', dest='textGraphics',
                      help='Display output as text only', default=False)
    parser.add_option('-q', '--quietTextGraphics', action='store_true', dest='quietGraphics',
                      help='Generate minimal output and no graphics', default=False)
    parser.add_option('-g', '--ghosts', dest='ghost',
                      help=default('the ghost agent TYPE in the ghostAgents module to use'),
                      metavar='TYPE', default='RandomGhost')
    parser.add_option('-k', '--numghosts', type='int', dest='numGhosts',
                      help=default('The maximum number of ghosts to use'), default=4)
    parser.add_option('-z', '--zoom', type='float', dest='zoom',
                      help=default('Zoom the size of the graphics window'), default=1.0)
    parser.add_option('-f', '--fixRandomSeed', action='store_true', dest='fixRandomSeed',
                      help='Fixes the random seed to always play the same game', default=False)
    parser.add_option('-r', '--recordActions', action='store_true', dest='record',
                      help='Writes game histories to a file (named by the time they were played)', default=False)
    parser.add_option('--replay', dest='gameToReplay',
                      help='A recorded game file (pickle) to replay', default=None)
    parser.add_option('-a', '--agentArgs', dest='agentArgs',
                      help='Comma separated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"')
    parser.add_option('-x', '--numTraining', dest='numTraining', type='int',
                      help=default('How many episodes are training (suppresses output)'), default=0)
    parser.add_option('--frameTime', dest='frameTime', type='float',
                      help=default('Time to delay between frames; <0 means keyboard'), default=0.1)
    parser.add_option('-c', '--catchExceptions', action='store_true', dest='catchExceptions',
                      help='Turns on exception handling and timeouts during games', default=False)
    parser.add_option('--timeout', dest='timeout', type='int',
                      help=default('Maximum length of time an agent can spend computing in a single game'), default=30)

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception(f'Command line input not understood: {otherjunk}')
    args = dict()

    # Fix the random seed
    if options.fixRandomSeed:
        random.seed('cs188')

    # Choose a layout
    args['layout'] = layout.getLayout(options.layout)
    if args['layout'] == None:
        raise Exception(f"The layout {options.layout} cannot be found")

    # Choose a Pacman agent
    noKeyboard = options.gameToReplay == None and (
        options.textGraphics or options.quietGraphics)
    pacmanType = loadAgent(options.pacman, noKeyboard)
    agentOpts = parseAgentArgs(options.agentArgs)
    if options.numTraining > 0:
        args['numTraining'] = options.numTraining
        if 'numTraining' not in agentOpts:
            agentOpts['numTraining'] = options.numTraining
    pacman = pacmanType(**agentOpts)  # Instantiate Pacman with agentArgs
    args['pacman'] = pacman

    # Don't display training games
    if 'numTrain' in agentOpts:
        options.numQuiet = int(agentOpts['numTrain'])
        options.numIgnore = int(agentOpts['numTrain'])

    # Choose a ghost agent
    ghostType = loadAgent(options.ghost, noKeyboard)
    args['ghosts'] = [ghostType(i+1) for i in range(options.numGhosts)]

    # Choose a display format
    if options.quietGraphics:
        import textDisplay
        args['display'] = textDisplay.NullGraphics()
    elif options.textGraphics:
        import textDisplay
        textDisplay.SLEEP_TIME = options.frameTime
        args['display'] = textDisplay.PacmanGraphics()
    else:
        import graphicsDisplay
        args['display'] = graphicsDisplay.PacmanGraphics(
            options.zoom, frameTime=options.frameTime)
    args['numGames'] = options.numGames
    args['record'] = options.record
    args['catchExceptions'] = options.catchExceptions
    args['timeout'] = options.timeout

    # Special case: recorded games don't use the runGames method or args structure
    if options.gameToReplay != None:
        print(f'Replaying recorded game {options.gameToReplay}.')
        import pickle
        f = open(options.gameToReplay)
        try:
            recorded = pickle.load(f)
        finally:
            f.close()
        recorded['display'] = args['display']
        replayGame(**recorded)
        sys.exit(0)

    return args


def loadAgent(pacman: str, nographics: bool) -> Any:
    """Load a Pacman or ghost agent class from a module.
    
    Searches through PYTHONPATH directories for agent modules and loads
    the specified agent class.
    
    Args:
        pacman: Name of the agent class to load
        nographics: Whether graphics are disabled
        
    Returns:
        The loaded agent class
        
    Raises:
        Exception: If agent cannot be found or loaded
    """
    pythonPathStr = os.path.expandvars("$PYTHONPATH")
    if pythonPathStr.find(';') == -1:
        pythonPathDirs = pythonPathStr.split(':')
    else:
        pythonPathDirs = pythonPathStr.split(';')
    pythonPathDirs.append('.')

    for moduleDir in pythonPathDirs:
        if not os.path.isdir(moduleDir):
            continue
        moduleNames = [f for f in os.listdir(moduleDir) if f.endswith('gents.py')]
        for modulename in moduleNames:
            try:
                module = __import__(modulename[:-3])
            except ImportError:
                continue
            if pacman in dir(module):
                if nographics and modulename == 'keyboardAgents.py':
                    raise Exception('Using the keyboard requires graphics (not text display)')
                return getattr(module, pacman)
    raise Exception(f'The agent {pacman} is not specified in any *Agents.py.')


def replayGame(layout: Any, actions: List[Tuple[int, str]], display: Any) -> None:
    """Replay a recorded game.
    
    Args:
        layout: The game layout
        actions: List of (agent_index, action) pairs representing game moves
        display: The game display interface
    """
    import pacmanAgents
    import ghostAgents
    rules = ClassicGameRules()
    agents = [pacmanAgents.GreedyAgent()] + [ghostAgents.RandomGhost(i+1)
                                            for i in range(layout.getNumGhosts())]
    game = rules.newGame(layout, agents[0], agents[1:], display)
    state = game.state
    display.initialize(state.data)

    for action in actions:
        # Execute the action
        state = state.generateSuccessor(*action)
        # Change the display
        display.update(state.data)
        # Allow for game specific conditions (winning, losing, etc.)
        rules.process(state, game)

    display.finish()


def runGames(layout: Any, pacman: Any, ghosts: List[Any], display: Any, 
            numGames: int, record: bool, numTraining: int = 0, 
            catchExceptions: bool = False, timeout: int = 30) -> List[Any]:
    """Run multiple games of Pacman.
    
    Args:
        layout: The game layout
        pacman: The Pacman agent
        ghosts: List of ghost agents
        display: The game display interface
        numGames: Number of games to run
        record: Whether to record games
        numTraining: Number of training games (no output)
        catchExceptions: Whether to catch agent exceptions
        timeout: Maximum time per agent move in seconds
        
    Returns:
        List of completed game instances
    """
    import __main__
    __main__.__dict__['_display'] = display

    rules = ClassicGameRules(timeout)
    games = []

    for i in range(numGames):
        beQuiet = i < numTraining
        if beQuiet:
            # Suppress output and graphics
            import textDisplay
            gameDisplay = textDisplay.NullGraphics()
            rules.quiet = True
        else:
            gameDisplay = display
            rules.quiet = False
        game = rules.newGame(layout, pacman, ghosts,
                           gameDisplay, beQuiet, catchExceptions)
        game.run()
        if not beQuiet:
            games.append(game)

        if record:
            import time
            import pickle
            fname = f'recorded-game-{i + 1}-{"-".join([str(t) for t in time.localtime()[1:6]])}'
            f = file(fname, 'w')
            components = {'layout': layout, 'actions': game.moveHistory}
            pickle.dump(components, f)
            f.close()

    if (numGames-numTraining) > 0:
        scores = [game.state.getScore() for game in games]
        wins = [game.state.isWin() for game in games]
        winRate = wins.count(True) / float(len(wins))
        print(f'Average Score: {sum(scores) / float(len(scores))}')
        print(f'Scores:        {", ".join([str(score) for score in scores])}')
        print(f'Win Rate:      {wins.count(True)}/{len(wins)} ({winRate:.2f})')
        print(f'Record:        {", ".join(["Loss" if not w else "Win" for w in wins])}')

    return games


if __name__ == '__main__':
    """Main entry point for running Pacman from command line.
    
    Run 'python pacman.py --help' to see available options.
    """
    args = readCommand(sys.argv[1:])  # Get game components based on input
    runGames(**args)

    # import cProfile
    # cProfile.run("runGames( **args )")
    pass
