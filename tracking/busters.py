# busters.py
# ----------
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
Busters.py is a vengeful variant of Pacman where Pacman hunts ghosts, but
cannot see them. Numbers at the bottom of the display are noisy distance
readings to each remaining ghost.

To play your first game, type 'python pacman.py' from the command line.
The keys are 'a', 's', 'd', and 'w' to move (or arrow keys). Have fun!
"""
from game import GameStateData
from game import Game
from game import Directions
from game import Actions
from game import Configuration
from util import nearestPoint
from util import manhattanDistance
import sys, util, types, time, random, layout, os
from typing import List, Dict, Tuple, Optional, Any, Union

########################################
# Parameters for noisy sensor readings #
########################################

SONAR_NOISE_RANGE = 15  # Must be odd
SONAR_MAX = (SONAR_NOISE_RANGE - 1) / 2
SONAR_NOISE_VALUES = [i - SONAR_MAX for i in range(SONAR_NOISE_RANGE)]
SONAR_DENOMINATOR = 2 ** SONAR_MAX + 2 ** (SONAR_MAX + 1) - 2.0
SONAR_NOISE_PROBS = [
    2 ** (SONAR_MAX - abs(v)) / SONAR_DENOMINATOR for v in SONAR_NOISE_VALUES
]


def getNoisyDistance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> Optional[float]:
    if pos2[1] == 1:
        return None
    distance = util.manhattanDistance(pos1, pos2)
    return max(0, distance + util.sample(SONAR_NOISE_PROBS, SONAR_NOISE_VALUES))


observationDistributions: Dict[float, util.Counter] = {}


def getObservationProbability(noisyDistance: float, trueDistance: float) -> float:
    """
    Returns the probability P(noisyDistance | trueDistance).

    Args:
        noisyDistance: The noisy distance reading
        trueDistance: The actual distance
        
    Returns:
        float: The probability of observing noisyDistance given trueDistance
    """
    global observationDistributions
    if noisyDistance not in observationDistributions:
        distribution = util.Counter()
        for error, prob in zip(SONAR_NOISE_VALUES, SONAR_NOISE_PROBS):
            distribution[max(1, noisyDistance - error)] += prob
        observationDistributions[noisyDistance] = distribution
    return observationDistributions[noisyDistance][trueDistance]


###################################################
# YOUR INTERFACE TO THE PACMAN WORLD: A GameState #
###################################################


class GameState:
    """
    A GameState specifies the full game state, including the food, capsules,
    agent configurations and score changes.

    GameStates are used by the Game object to capture the actual state of the game and
    can be used by agents to reason about the game.

    Much of the information in a GameState is stored in a GameStateData object. We
    strongly suggest that you access that data via the accessor methods below rather
    than referring to the GameStateData object directly.

    Note that in classic Pacman, Pacman is always agent 0.
    """

    ####################################################
    # Accessor methods: use these to access state data #
    ####################################################

    def getLegalActions(self, agentIndex: int = 0) -> List[str]:
        """
        Returns the legal actions for the agent specified.

        Args:
            agentIndex: Index of the agent (0 for Pacman)
            
        Returns:
            List of legal action strings
        """
        if self.isWin() or self.isLose():
            return []

        if agentIndex == 0:  # Pacman is moving
            return PacmanRules.getLegalActions(self)
        else:
            return GhostRules.getLegalActions(self, agentIndex)

    def getResult(self, agentIndex: int, action: str) -> 'GameState':
        """
        Returns the state after the specified agent takes the action.

        Args:
            agentIndex: Index of the agent taking the action
            action: The action being taken
            
        Returns:
            The successor GameState
            
        Raises:
            Exception if called on a terminal state
        """
        # Check that successors exist
        if self.isWin() or self.isLose():
            raise Exception("Can't generate a result of a terminal state.")

        # Copy current state
        state = GameState(self)

        # Let agent's logic deal with its action's effects on the board
        if agentIndex == 0:  # Pacman is moving
            state.data._eaten = [False for i in range(state.getNumAgents())]
            PacmanRules.applyAction(state, action)
        else:  # A ghost is moving
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
        p = state.getPacmanPosition()
        state.data.ghostDistances = [
            getNoisyDistance(p, state.getGhostPosition(i))
            for i in range(1, state.getNumAgents())
        ]
        if agentIndex == self.getNumAgents() - 1:
            state.numMoves += 1
        return state

    def getLegalPacmanActions(self) -> List[str]:
        return self.getLegalActions(0)

    def getPacmanResult(self, action: str) -> 'GameState':
        """
        Generates the result state after the specified pacman action

        Args:
            action: The action being taken by Pacman
            
        Returns:
            The successor GameState
        """
        return self.getResult(0, action)

    def getPacmanState(self) -> GameStateData:
        """
        Returns an AgentState object for pacman (in game.py)

        state.pos gives the current position
        state.direction gives the travel vector
        
        Returns:
            Copy of Pacman's agent state
        """
        return self.data.agentStates[0].copy()

    def getPacmanPosition(self) -> Tuple[int, int]:
        return self.data.agentStates[0].getPosition()

    def getNumAgents(self) -> int:
        return len(self.data.agentStates)

    def getScore(self) -> float:
        return self.data.score

    def getCapsules(self) -> List[Tuple[int, int]]:
        """
        Returns a list of positions (x,y) of the remaining capsules.
        """
        return self.data.capsules

    def getNumFood(self) -> int:
        return self.data.food.count()

    def getFood(self) -> 'Grid':
        """
        Returns a Grid of boolean food indicator variables.

        Grids can be accessed via list notation, so to check
        if there is food at (x,y), just call

        currentFood = state.getFood()
        if currentFood[x][y] == True: ...
        """
        return self.data.food

    def getWalls(self) -> 'Grid':
        """
        Returns a Grid of boolean wall indicator variables.

        Grids can be accessed via list notation, so to check
        if there is a wall at (x,y), just call

        walls = state.getWalls()
        if walls[x][y] == True: ...
        """
        return self.data.layout.walls

    def hasFood(self, x: int, y: int) -> bool:
        return self.data.food[x][y]

    def hasWall(self, x: int, y: int) -> bool:
        return self.data.layout.walls[x][y]

    ##############################
    # Additions for Busters Pacman #
    ##############################

    def getLivingGhosts(self) -> List[bool]:
        """
        Returns a list of booleans indicating which ghosts are not yet captured.

        The first entry (a placeholder for Pacman's index) is always False.
        """
        return self.livingGhosts

    def setGhostNotLiving(self, index: int) -> None:
        self.livingGhosts[index] = False

    def isLose(self) -> bool:
        return self.maxMoves > 0 and self.numMoves >= self.maxMoves

    def isWin(self) -> bool:
        return self.livingGhosts.count(True) == 0

    def getNoisyGhostDistances(self) -> List[Optional[float]]:
        """
        Returns a noisy distance to each ghost.
        """
        return self.data.ghostDistances

    #############################################
    #             Helper methods:               #
    # You shouldn't need to call these directly #
    #############################################

    def __init__(self, prevState: Optional['GameState'] = None):
        """
        Generates a new state by copying information from its predecessor.
        """
        if prevState != None:
            self.data = GameStateData(prevState.data)
            self.livingGhosts = prevState.livingGhosts[:]
            self.numMoves = prevState.numMoves
            self.maxMoves = prevState.maxMoves
        else:  # Initial state
            self.data = GameStateData()
            self.numMoves = 0
            self.maxMoves = -1
        self.data.ghostDistances = []

    def deepCopy(self) -> 'GameState':
        state = GameState(self)
        state.data = self.data.deepCopy()
        state.data.ghostDistances = self.data.ghostDistances
        return state

    def __eq__(self, other: Any) -> bool:
        """
        Allows two states to be compared.
        """
        if other is None:
            return False
        return self.data == other.data

    def __hash__(self) -> int:
        """
        Allows states to be keys of dictionaries.
        """
        return hash(str(self))

    def __str__(self) -> str:
        return str(self.data)

    def initialize(self, layout: 'Layout', numGhostAgents: int = 1000) -> None:
        """
        Creates an initial game state from a layout array (see layout.py).
        """
        self.data.initialize(layout, numGhostAgents)
        self.livingGhosts = [False] + [True for i in range(numGhostAgents)]
        self.data.ghostDistances = [
            getNoisyDistance(self.getPacmanPosition(), self.getGhostPosition(i))
            for i in range(1, self.getNumAgents())
        ]

    def getGhostPosition(self, agentIndex: int) -> Tuple[int, int]:
        if agentIndex == 0:
            raise Exception("Pacman's index passed to getGhostPosition")
        return self.data.agentStates[agentIndex].getPosition()

    def getGhostState(self, agentIndex: int) -> GameStateData:
        if agentIndex == 0:
            raise Exception("Pacman's index passed to getGhostPosition")
        return self.data.agentStates[agentIndex]


############################################################################
#                     THE HIDDEN SECRETS OF PACMAN                         #
#                                                                          #
# You shouldn't need to look through the code in this section of the file. #
############################################################################

COLLISION_TOLERANCE = 0.7  # How close ghosts must be to Pacman to kill
TIME_PENALTY = 1  # Number of points lost each round


class BustersGameRules:
    """
    These game rules manage the control flow of a game, deciding when
    and how the game starts and ends.
    """

    def newGame(
        self,
        layout: 'Layout',
        pacmanAgent: 'Agent',
        ghostAgents: List['Agent'],
        display: 'Display',
        maxMoves: int = -1,
    ) -> Game:
        agents = [pacmanAgent] + ghostAgents
        initState = GameState()
        initState.initialize(layout, len(ghostAgents))
        game = Game(agents, display, self)
        game.state = initState
        game.state.maxMoves = maxMoves
        return game

    def process(self, state: GameState, game: Game) -> None:
        """
        Checks to see whether it is time to end the game.
        """
        if state.isWin():
            self.win(state, game)
        if state.isLose():
            self.lose(state, game)

    def win(self, state: GameState, game: Game) -> None:
        game.gameOver = True

    def lose(self, state: GameState, game: Game) -> None:
        game.gameOver = True


class PacmanRules:
    """
    These functions govern how pacman interacts with his environment under
    the classic game rules.
    """

    @staticmethod
    def getLegalActions(state: GameState) -> List[str]:
        """
        Returns a list of possible actions.
        """
        return Actions.getPossibleActions(
            state.getPacmanState().configuration, state.data.layout.walls
        )

    @staticmethod
    def applyAction(state: GameState, action: str) -> None:
        """
        Edits the state to reflect the results of the action.
        """
        legal = PacmanRules.getLegalActions(state)
        if action not in legal:
            raise Exception(f"Illegal action {action}")

        pacmanState = state.data.agentStates[0]

        # Update Configuration
        vector = Actions.directionToVector(action, 1)
        pacmanState.configuration = pacmanState.configuration.generateSuccessor(vector)


class GhostRules:
    """
    These functions dictate how ghosts interact with their environment.
    """

    @staticmethod
    def getLegalActions(state: GameState, ghostIndex: int) -> List[str]:
        conf = state.getGhostState(ghostIndex).configuration
        return Actions.getPossibleActions(conf, state.data.layout.walls)

    @staticmethod
    def applyAction(state: GameState, action: str, ghostIndex: int) -> None:
        legal = GhostRules.getLegalActions(state, ghostIndex)
        if action not in legal:
            raise Exception(f"Illegal ghost action: {action}")

        ghostState = state.data.agentStates[ghostIndex]
        vector = Actions.directionToVector(action, 1)
        ghostState.configuration = ghostState.configuration.generateSuccessor(vector)

    @staticmethod
    def decrementTimer(ghostState: GameStateData) -> None:
        timer = ghostState.scaredTimer
        if timer == 1:
            ghostState.configuration.pos = nearestPoint(ghostState.configuration.pos)
        ghostState.scaredTimer = max(0, timer - 1)

    @staticmethod
    def checkDeath(state: GameState, agentIndex: int) -> None:
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

    @staticmethod
    def collide(state: GameState, ghostState: GameStateData, agentIndex: int) -> None:
        state.data.scoreChange += 200
        GhostRules.placeGhost(ghostState, agentIndex)
        # Added for first-person
        state.data._eaten[agentIndex] = True
        state.setGhostNotLiving(agentIndex)

    @staticmethod
    def canKill(pacmanPosition: Tuple[int, int], ghostPosition: Tuple[int, int]) -> bool:
        return manhattanDistance(ghostPosition, pacmanPosition) <= COLLISION_TOLERANCE

    @staticmethod
    def placeGhost(ghostState: GameStateData, agentIndex: int) -> None:
        pos = (agentIndex * 2 - 1, 1)
        direction = Directions.STOP
        ghostState.configuration = Configuration(pos, direction)


#############################
# FRAMEWORK TO START A GAME #
#############################


def default(str: str) -> str:
    return f"{str} [Default: %default]"


def parseAgentArgs(str: Optional[str]) -> Dict[str, Any]:
    if str == None:
        return {}
    pieces = str.split(",")
    opts = {}
    for p in pieces:
        if "=" in p:
            key, val = p.split("=")
        else:
            key, val = p, 1
        opts[key] = val
    return opts


def readCommand(argv: List[str]) -> Dict[str, Any]:
    """
    Processes the command used to run pacman from the command line.
    """
    from optparse import OptionParser

    usageStr = """
    USAGE:      python busters.py <options>
    EXAMPLE:    python busters.py --layout bigHunt
                  - starts an interactive game on a big board
    """
    parser = OptionParser(usageStr)

    parser.add_option(
        "-n",
        "--numGames",
        dest="numGames",
        type="int",
        help=default("the number of GAMES to play"),
        metavar="GAMES",
        default=1,
    )
    parser.add_option(
        "-l",
        "--layout",
        dest="layout",
        help=default("the LAYOUT_FILE from which to load the map layout"),
        metavar="LAYOUT_FILE",
        default="oneHunt",
    )
    parser.add_option(
        "-p",
        "--pacman",
        dest="pacman",
        help=default("the agent TYPE in the pacmanAgents module to use"),
        metavar="TYPE",
        default="BustersKeyboardAgent",
    )
    parser.add_option(
        "-a",
        "--agentArgs",
        dest="agentArgs",
        help='Comma separated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"',
    )
    parser.add_option(
        "-g",
        "--ghosts",
        dest="ghost",
        help=default("the ghost agent TYPE in the ghostAgents module to use"),
        metavar="TYPE",
        default="RandomGhost",
    )
    parser.add_option(
        "-q",
        "--quietTextGraphics",
        action="store_true",
        dest="quietGraphics",
        help="Generate minimal output and no graphics",
        default=False,
    )
    parser.add_option(
        "-k",
        "--numghosts",
        type="int",
        dest="numGhosts",
        help=default("The maximum number of ghosts to use"),
        default=4,
    )
    parser.add_option(
        "-z",
        "--zoom",
        type="float",
        dest="zoom",
        help=default("Zoom the size of the graphics window"),
        default=1.0,
    )
    parser.add_option(
        "-f",
        "--fixRandomSeed",
        action="store_true",
        dest="fixRandomSeed",
        help="Fixes the random seed to always play the same game",
        default=False,
    )
    parser.add_option(
        "-s",
        "--showGhosts",
        action="store_true",
        dest="showGhosts",
        help="Renders the ghosts in the display (cheating)",
        default=False,
    )
    parser.add_option(
        "-t",
        "--frameTime",
        dest="frameTime",
        type="float",
        help=default("Time to delay between frames; <0 means keyboard"),
        default=0.1,
    )

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception(f"Command line input not understood: {otherjunk}")
    args = dict()

    # Fix the random seed
    if options.fixRandomSeed:
        random.seed("bustersPacman")

    # Choose a layout
    args["layout"] = layout.getLayout(options.layout)
    if args["layout"] == None:
        raise Exception(f"The layout {options.layout} cannot be found")

    # Choose a ghost agent
    ghostType = loadAgent(options.ghost, options.quietGraphics)
    args["ghosts"] = [ghostType(i + 1) for i in range(options.numGhosts)]

    # Choose a Pacman agent
    noKeyboard = options.quietGraphics
    pacmanType = loadAgent(options.pacman, noKeyboard)
    agentOpts = parseAgentArgs(options.agentArgs)
    agentOpts["ghostAgents"] = args["ghosts"]
    pacman = pacmanType(**agentOpts)  # Instantiate Pacman with agentArgs
    args["pacman"] = pacman

    import graphicsDisplay

    args["display"] = graphicsDisplay.FirstPersonPacmanGraphics(
        options.zoom, options.showGhosts, frameTime=options.frameTime
    )
    args["numGames"] = options.numGames

    return args


def loadAgent(pacman: str, nographics: bool) -> Any:
    # Looks through all pythonPath Directories for the right module,
    pythonPathStr = os.path.expandvars("$PYTHONPATH")
    if pythonPathStr.find(";") == -1:
        pythonPathDirs = pythonPathStr.split(":")
    else:
        pythonPathDirs = pythonPathStr.split(";")
    pythonPathDirs.append(".")

    for moduleDir in pythonPathDirs:
        if not os.path.isdir(moduleDir):
            continue
        moduleNames = [f for f in os.listdir(moduleDir) if f.endswith("gents.py")]
        for modulename in moduleNames:
            try:
                module = __import__(modulename[:-3])
                if pacman in dir(module):
                    if nographics and modulename == "keyboardAgents.py":
                        raise Exception(
                            "Using the keyboard requires graphics (not text display)"
                        )
                    return getattr(module, pacman)
            except ImportError:
                continue
    raise Exception(f"The agent {pacman} is not specified in any *Agents.py.")


def runGames(
    layout: 'Layout',
    pacman: 'Agent',
    ghosts: List['Agent'],
    display: 'Display',
    numGames: int,
    maxMoves: int = -1,
) -> List[Game]:
    # Hack for agents writing to the display
    import __main__

    __main__.__dict__["_display"] = display

    rules = BustersGameRules()
    games = []

    for i in range(numGames):
        game = rules.newGame(layout, pacman, ghosts, display, maxMoves)
        game.run()
        games.append(game)

    if numGames > 1:
        scores = [game.state.getScore() for game in games]
        wins = [game.state.isWin() for game in games]
        winRate = wins.count(True) / float(len(wins))
        print(f"Average Score: {sum(scores) / float(len(scores))}")
        print(f"Scores:        {', '.join([str(score) for score in scores])}")
        print(f"Win Rate:      {wins.count(True)}/{len(wins)} ({winRate:.2f})")
        print(f"Record:        {', '.join(['Loss' if not w else 'Win' for w in wins])}")

    return games


if __name__ == "__main__":
    """
    The main function called when busters.py is run
    from the command line:

    > python busters.py

    See the usage string for more details.

    > python busters.py --help
    """
    args = readCommand(sys.argv[1:])  # Get game components based on input
    runGames(**args)