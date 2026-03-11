"""
Grid-based Markov Decision Process environment.

This module implements a grid world environment that follows the MDP interface.
The environment consists of:
- A 2D grid where an agent can move in cardinal directions
- States represented as (x,y) coordinates
- Actions: north, south, east, west
- Stochastic transitions with configurable noise
- Rewards for reaching goals and living penalties
- Terminal states that end episodes

The grid world provides a simple testbed for reinforcement learning algorithms
like value iteration and Q-learning. Key features include:
- Configurable grid layouts and reward structures
- Noisy movement dynamics
- Visual display capabilities
- Integration with the MDP interface

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added type hints
- Added detailed class and method descriptions
- Added Python version compatibility note
- Added last modified date and modifier
- Verified Python 3.13 compatibility


# gridworld.py
# ------------
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

import random
import sys
import mdp
import environment
import util
import optparse
from typing import List, Tuple, Optional, Any, Dict, Union

class Gridworld(mdp.MarkovDecisionProcess):
    """
    A grid-based world that implements the MarkovDecisionProcess interface.
    The grid represents a 2D environment where an agent can move in four directions.
    Some cells may contain rewards, walls, or terminal states.
    """
    def __init__(self, grid: Union[List[List[Any]], 'Grid']) -> None:
        # layout
        if isinstance(grid, list): grid = makeGrid(grid)
        self.grid = grid

        # parameters
        self.livingReward = 0.0
        self.noise = 0.2

    def setLivingReward(self, reward: float) -> None:
        """
        Sets the reward for living/moving to a non-terminal state.
        
        Args:
            reward: The reward value to set. Typically negative to encourage reaching the goal.
        """
        self.livingReward = reward

    def setNoise(self, noise: float) -> None:
        """
        Sets the probability of the agent moving in an unintended direction.
        
        Args:
            noise: A value between 0 and 1 representing the probability of moving in an unintended direction.
        """
        self.noise = noise

    def getPossibleActions(self, state: Tuple[int, int]) -> Tuple[str, ...]:
        """
        Returns list of valid actions for the given state.

        Args:
            state: A tuple (x,y) representing the current position

        Returns:
            A tuple of strings representing valid actions ('north', 'south', 'east', 'west', 'exit')
            Empty tuple if state is terminal
        """
        if state == self.grid.terminalState:
            return ()
        x,y = state
        if isinstance(self.grid[x][y], (int, float)):
            return ('exit',)
        return ('north','west','south','east')

    def getStates(self) -> List[Union[Tuple[int, int], str]]:
        """
        Returns list of all states in the grid.

        Returns:
            List containing the terminal state and all valid (x,y) grid positions
        """
        # The true terminal state.
        states = [self.grid.terminalState]
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                if self.grid[x][y] != '#':
                    state = (x,y)
                    states.append(state)
        return states

    def getReward(self, state: Tuple[int, int], action: str, nextState: Tuple[int, int]) -> float:
        """
        Get reward for state, action, nextState transition.

        Args:
            state: Current (x,y) position
            action: Action taken
            nextState: Resulting (x,y) position

        Returns:
            The reward value for this transition
        """
        if state == self.grid.terminalState:
            return 0.0
        x, y = state
        cell = self.grid[x][y]
        if isinstance(cell, (int, float)):
            return cell
        return self.livingReward

    def getStartState(self) -> Tuple[int, int]:
        """
        Returns the starting position marked with 'S' in the grid.

        Returns:
            Tuple (x,y) of starting coordinates

        Raises:
            Exception if no start state exists
        """
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                if self.grid[x][y] == 'S':
                    return (x, y)
        raise Exception('Grid has no start state')

    def isTerminal(self, state: Union[Tuple[int, int], str]) -> bool:
        """
        Checks if the given state is terminal.
        Only the TERMINAL_STATE is considered truly terminal.
        Other "exit" states lead to TERMINAL_STATE.

        Args:
            state: Position to check

        Returns:
            True if state is terminal, False otherwise
        """
        return state == self.grid.terminalState

    def getTransitionStatesAndProbs(self, state: Tuple[int, int], action: str) -> List[Tuple[Union[Tuple[int, int], str], float]]:
        """
        Returns list of possible next states and their probabilities when taking an action from a state.

        Args:
            state: Current (x,y) position
            action: Action to take

        Returns:
            List of (nextState, probability) pairs

        Raises:
            Exception for illegal actions
        """

        if action not in self.getPossibleActions(state):
            raise Exception("Illegal action!")

        if self.isTerminal(state):
            return []

        x, y = state

        if isinstance(self.grid[x][y], (int, float)):
            termState = self.grid.terminalState
            return [(termState, 1.0)]

        successors = []

        northState = (self.__isAllowed(y+1,x) and (x,y+1)) or state
        westState = (self.__isAllowed(y,x-1) and (x-1,y)) or state
        southState = (self.__isAllowed(y-1,x) and (x,y-1)) or state
        eastState = (self.__isAllowed(y,x+1) and (x+1,y)) or state

        if action == 'north' or action == 'south':
            if action == 'north':
                successors.append((northState,1-self.noise))
            else:
                successors.append((southState,1-self.noise))

            massLeft = self.noise
            successors.append((westState,massLeft/2.0))
            successors.append((eastState,massLeft/2.0))

        if action == 'west' or action == 'east':
            if action == 'west':
                successors.append((westState,1-self.noise))
            else:
                successors.append((eastState,1-self.noise))

            massLeft = self.noise
            successors.append((northState,massLeft/2.0))
            successors.append((southState,massLeft/2.0))

        successors = self.__aggregate(successors)

        return successors

    def __aggregate(self, statesAndProbs: List[Tuple[Union[Tuple[int, int], str], float]]) -> List[Tuple[Union[Tuple[int, int], str], float]]:
        counter = util.Counter()
        for state, prob in statesAndProbs:
            counter[state] += prob
        newStatesAndProbs = []
        for state, prob in list(counter.items()):
            newStatesAndProbs.append((state, prob))
        return newStatesAndProbs

    def __isAllowed(self, y: int, x: int) -> bool:
        if y < 0 or y >= self.grid.height: return False
        if x < 0 or x >= self.grid.width: return False
        return self.grid[x][y] != '#'

class GridworldEnvironment(environment.Environment):

    def __init__(self, gridWorld: Gridworld) -> None:
        self.gridWorld = gridWorld
        self.reset()

    def getCurrentState(self) -> Tuple[int, int]:
        return self.state

    def getPossibleActions(self, state: Tuple[int, int]) -> Tuple[str, ...]:
        return self.gridWorld.getPossibleActions(state)

    def doAction(self, action: str) -> Tuple[Tuple[int, int], float]:
        state = self.getCurrentState()
        (nextState, reward) = self.getRandomNextState(state, action)
        self.state = nextState
        return (nextState, reward)

    def getRandomNextState(self, state: Tuple[int, int], action: str, randObj: Optional[random.Random] = None) -> Tuple[Tuple[int, int], float]:
        rand = -1.0
        if randObj is None:
            rand = random.random()
        else:
            rand = randObj.random()
        sum = 0.0
        successors = self.gridWorld.getTransitionStatesAndProbs(state, action)
        for nextState, prob in successors:
            sum += prob
            if sum > 1.0:
                raise Exception('Total transition probability more than one; sample failure.')
            if rand < sum:
                reward = self.gridWorld.getReward(state, action, nextState)
                return (nextState, reward)
        raise Exception('Total transition probability less than one; sample failure.')

    def reset(self) -> None:
        self.state = self.gridWorld.getStartState()

class Grid:
    """
    A 2-dimensional array of immutables backed by a list of lists. Data is accessed
    via grid[x][y] where (x,y) are cartesian coordinates with x horizontal,
    y vertical and the origin (0,0) in the bottom left corner.

    The __str__ method constructs an output that is oriented appropriately.
    """
    def __init__(self, width: int, height: int, initialValue: Any = ' ') -> None:
        self.width = width
        self.height = height
        self.data = [[initialValue for y in range(height)] for x in range(width)]
        self.terminalState = 'TERMINAL_STATE'

    def __getitem__(self, i: int) -> List[Any]:
        return self.data[i]

    def __setitem__(self, key: int, item: List[Any]) -> None:
        self.data[key] = item

    def __eq__(self, other: Optional['Grid']) -> bool:
        if other == None: return False
        return self.data == other.data

    def __hash__(self) -> int:
        return hash(self.data)

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

    def _getLegacyText(self) -> List[List[Any]]:
        t = [[self.data[x][y] for x in range(self.width)] for y in range(self.height)]
        t.reverse()
        return t

    def __str__(self) -> str:
        return str(self._getLegacyText())

def makeGrid(gridString: List[str]) -> Grid:
    width, height = len(gridString[0]), len(gridString)
    grid = Grid(width, height)
    for ybar, line in enumerate(gridString):
        y = height - ybar - 1
        for x, el in enumerate(line):
            grid[x][y] = el
    return grid

def getCliffGrid() -> Gridworld:
    grid = [[' ',' ',' ',' ',' '],
            ['S',' ',' ',' ',10],
            [-100,-100, -100, -100, -100]]
    return Gridworld(makeGrid(grid))

def getCliffGrid2() -> Gridworld:
    grid = [[' ',' ',' ',' ',' '],
            [8,'S',' ',' ',10],
            [-100,-100, -100, -100, -100]]
    return Gridworld(grid)

def getDiscountGrid() -> Gridworld:
    grid = [[' ',' ',' ',' ',' '],
            [' ','#',' ',' ',' '],
            [' ','#', 1,'#', 10],
            ['S',' ',' ',' ',' '],
            [-10,-10, -10, -10, -10]]
    return Gridworld(grid)

def getBridgeGrid() -> Gridworld:
    grid = [[ '#',-100, -100, -100, -100, -100, '#'],
            [   1, 'S',  ' ',  ' ',  ' ',  ' ',  10],
            [ '#',-100, -100, -100, -100, -100, '#']]
    return Gridworld(grid)

def getBookGrid() -> Gridworld:
    grid = [[' ',' ',' ',+1],
            [' ','#',' ',-1],
            ['S',' ',' ',' ']]
    return Gridworld(grid)

def getMazeGrid() -> Gridworld:
    grid = [[' ',' ',' ',+1],
            ['#','#',' ','#'],
            [' ','#',' ',' '],
            [' ','#','#',' '],
            ['S',' ',' ',' ']]
    return Gridworld(grid)

def getExamGrid() -> Gridworld:
    grid = [[' ',' ',' ',+1],
            [' ','#',' ', ' '],
            ['S',' ',' ', +100]]
    return Gridworld(grid)

def getUserAction(state: Tuple[int, int], actionFunction: Any) -> str:
    """
    Get an action from the user (rather than the agent).
    Used for debugging and lecture demos.

    Args:
        state: Current state
        actionFunction: Function that returns valid actions for state

    Returns:
        Action string based on user keyboard input
    """
    import graphicsUtils
    action = None
    while True:
        keys = graphicsUtils.wait_for_keys()
        if 'Up' in keys: action = 'north'
        if 'Down' in keys: action = 'south'
        if 'Left' in keys: action = 'west'
        if 'Right' in keys: action = 'east'
        if 'q' in keys: sys.exit(0)
        if action == None: continue
        break
    actions = actionFunction(state)
    if action not in actions:
        action = actions[0]
    return action

def printString(x: str) -> None: print(x)

def runEpisode(agent: Any, environment: GridworldEnvironment, discount: float, decision: Any, display: Any, message: Any, pause: Any, episode: int) -> float:
    returns = 0
    totalDiscount = 1.0
    environment.reset()
    if 'startEpisode' in dir(agent): agent.startEpisode()
    message(f"BEGINNING EPISODE: {episode}\n")
    while True:

        # DISPLAY CURRENT STATE
        state = environment.getCurrentState()
        display(state)
        pause()

        # END IF IN A TERMINAL STATE
        actions = environment.getPossibleActions(state)
        if len(actions) == 0:
            message(f"EPISODE {episode} COMPLETE: RETURN WAS {returns}\n")
            return returns

        # GET ACTION (USUALLY FROM AGENT)
        action = decision(state)
        if action == None:
            raise Exception('Error: Agent returned None action')

        # EXECUTE ACTION
        nextState, reward = environment.doAction(action)
        message(f"Started in state: {state}\nTook action: {action}\nEnded in state: {nextState}\nGot reward: {reward}\n")
        # UPDATE LEARNER
        if 'observeTransition' in dir(agent):
            agent.observeTransition(state, action, nextState, reward)

        returns += reward * totalDiscount
        totalDiscount *= discount

    if 'stopEpisode' in dir(agent):
        agent.stopEpisode()

def parseOptions() -> optparse.Values:
    optParser = optparse.OptionParser()
    optParser.add_option('-d', '--discount',action='store',
                         type='float',dest='discount',default=0.9,
                         help='Discount on future (default %default)')
    optParser.add_option('-r', '--livingReward',action='store',
                         type='float',dest='livingReward',default=0.0,
                         metavar="R", help='Reward for living for a time step (default %default)')
    optParser.add_option('-n', '--noise',action='store',
                         type='float',dest='noise',default=0.2,
                         metavar="P", help='How often action results in ' +
                         'unintended direction (default %default)' )
    optParser.add_option('-e', '--epsilon',action='store',
                         type='float',dest='epsilon',default=0.3,
                         metavar="E", help='Chance of taking a random action in q-learning (default %default)')
    optParser.add_option('-l', '--learningRate',action='store',
                         type='float',dest='learningRate',default=0.5,
                         metavar="P", help='TD learning rate (default %default)' )
    optParser.add_option('-i', '--iterations',action='store',
                         type='int',dest='iters',default=10,
                         metavar="K", help='Number of rounds of value iteration (default %default)')
    optParser.add_option('-k', '--episodes',action='store',
                         type='int',dest='episodes',default=1,
                         metavar="K", help='Number of epsiodes of the MDP to run (default %default)')
    optParser.add_option('-g', '--grid',action='store',
                         metavar="G", type='string',dest='grid',default="BookGrid",
                         help='Grid to use (case sensitive; options are BookGrid, BridgeGrid, CliffGrid, MazeGrid, default %default)' )
    optParser.add_option('-w', '--windowSize', metavar="X", type='int',dest='gridSize',default=150,
                         help='Request a window width of X pixels *per grid cell* (default %default)')
    optParser.add_option('-a', '--agent',action='store', metavar="A",
                         type='string',dest='agent',default="random",
                         help='Agent type (options are \'random\', \'value\' and \'q\', default %default)')
    optParser.add_option('-t', '--text',action='store_true',
                         dest='textDisplay',default=False,
                         help='Use text-only ASCII display')
    optParser.add_option('-p', '--pause',action='store_true',
                         dest='pause',default=False,
                         help='Pause GUI after each time step when running the MDP')
    optParser.add_option('-q', '--quiet',action='store_true',
                         dest='quiet',default=False,
                         help='Skip display of any learning episodes')
    optParser.add_option('-s', '--speed',action='store', metavar="S", type=float,
                         dest='speed',default=1.0,
                         help='Speed of animation, S > 1.0 is faster, 0.0 < S < 1.0 is slower (default %default)')
    optParser.add_option('-m', '--manual',action='store_true',
                         dest='manual',default=False,
                         help='Manually control agent')
    optParser.add_option('-v', '--valueSteps',action='store_true' ,default=False,
                         help='Display each step of value iteration')

    opts, args = optParser.parse_args()

    if opts.manual and opts.agent != 'q':
        print('## Disabling Agents in Manual Mode (-m) ##')
        opts.agent = None

    # MANAGE CONFLICTS
    if opts.textDisplay or opts.quiet:
    # if opts.quiet:
        opts.pause = False
        # opts.manual = False

    if opts.manual:
        opts.pause = True

    return opts


if __name__ == '__main__':

    opts = parseOptions()

    ###########################
    # GET THE GRIDWORLD
    ###########################

    import gridworld
    mdpFunction = getattr(gridworld, "get"+opts.grid)
    mdp = mdpFunction()
    mdp.setLivingReward(opts.livingReward)
    mdp.setNoise(opts.noise)
    env = gridworld.GridworldEnvironment(mdp)


    ###########################
    # GET THE DISPLAY ADAPTER
    ###########################

    import textGridworldDisplay
    display = textGridworldDisplay.TextGridworldDisplay(mdp)
    if not opts.textDisplay:
        import graphicsGridworldDisplay
        display = graphicsGridworldDisplay.GraphicsGridworldDisplay(mdp, opts.gridSize, opts.speed)
    try:
        display.start()
    except KeyboardInterrupt:
        sys.exit(0)

    ###########################
    # GET THE AGENT
    ###########################

    import valueIterationAgents, qlearningAgents
    a = None
    if opts.agent == 'value':
        a = valueIterationAgents.ValueIterationAgent(mdp, opts.discount, opts.iters)
    elif opts.agent == 'q':
        #env.getPossibleActions, opts.discount, opts.learningRate, opts.epsilon
        #simulationFn = lambda agent, state: simulation.GridworldSimulation(agent,state,mdp)
        gridWorldEnv = GridworldEnvironment(mdp)
        actionFn = lambda state: mdp.getPossibleActions(state)
        qLearnOpts = {'gamma': opts.discount,
                      'alpha': opts.learningRate,
                      'epsilon': opts.epsilon,
                      'actionFn': actionFn}
        a = qlearningAgents.QLearningAgent(**qLearnOpts)
    elif opts.agent == 'random':
        # # No reason to use the random agent without episodes
        if opts.episodes == 0:
            opts.episodes = 10
        class RandomAgent:
            def getAction(self, state):
                return random.choice(mdp.getPossibleActions(state))
            def getValue(self, state):
                return 0.0
            def getQValue(self, state, action):
                return 0.0
            def getPolicy(self, state):
                "NOTE: 'random' is a special policy value; don't use it in your code."
                return 'random'
            def update(self, state, action, nextState, reward):
                pass
        a = RandomAgent()
    elif opts.agent == 'asynchvalue':
        a = valueIterationAgents.AsynchronousValueIterationAgent(mdp, opts.discount, opts.iters)
    elif opts.agent == 'priosweepvalue':
        a = valueIterationAgents.PrioritizedSweepingValueIterationAgent(mdp, opts.discount, opts.iters)
    else:
        if not opts.manual: raise Exception('Unknown agent type: '+opts.agent)


    ###########################
    # RUN EPISODES
    ###########################
    # DISPLAY Q/V VALUES BEFORE SIMULATION OF EPISODES
    try:
        if not opts.manual and opts.agent in ('value', 'asynchvalue', 'priosweepvalue'):
            if opts.valueSteps:
                for i in range(opts.iters):
                    tempAgent = valueIterationAgents.ValueIterationAgent(mdp, opts.discount, i)
                    display.displayValues(tempAgent, message = f"VALUES AFTER {i} ITERATIONS")
                    display.pause()

            display.displayValues(a, message = f"VALUES AFTER {opts.iters} ITERATIONS")
            display.pause()
            display.displayQValues(a, message = f"Q-VALUES AFTER {opts.iters} ITERATIONS")
            display.pause()
    except KeyboardInterrupt:
        sys.exit(0)



    # FIGURE OUT WHAT TO DISPLAY EACH TIME STEP (IF ANYTHING)
    displayCallback = lambda x: None
    if not opts.quiet:
        if opts.manual and opts.agent == None:
            displayCallback = lambda state: display.displayNullValues(state)
        else:
            if opts.agent in ('random', 'value', 'asynchvalue', 'priosweepvalue'):
                displayCallback = lambda state: display.displayValues(a, state, "CURRENT VALUES")
            if opts.agent == 'q': displayCallback = lambda state: display.displayQValues(a, state, "CURRENT Q-VALUES")

    messageCallback = lambda x: printString(x)
    if opts.quiet:
        messageCallback = lambda x: None

    # FIGURE OUT WHETHER TO WAIT FOR A KEY PRESS AFTER EACH TIME STEP
    pauseCallback = lambda : None
    if opts.pause:
        pauseCallback = lambda : display.pause()

    # FIGURE OUT WHETHER THE USER WANTS MANUAL CONTROL (FOR DEBUGGING AND DEMOS)
    if opts.manual:
        decisionCallback = lambda state : getUserAction(state, mdp.getPossibleActions)
    else:
        decisionCallback = a.getAction

    # RUN EPISODES
    if opts.episodes > 0:
        print()
        print("RUNNING", opts.episodes, "EPISODES")
        print()
    returns = 0
    for episode in range(1, opts.episodes+1):
        returns += runEpisode(a, env, opts.discount, decisionCallback, displayCallback, messageCallback, pauseCallback, episode)
    if opts.episodes > 0:
        print()
        print(f"AVERAGE RETURNS FROM START STATE: {(returns+0.0) / opts.episodes}")
        print()
        print()

    # DISPLAY POST-LEARNING VALUES / Q-VALUES
    if opts.agent == 'q' and not opts.manual:
        try:
            display.displayQValues(a, message = f"Q-VALUES AFTER {opts.episodes} EPISODES")
            display.pause()
            display.displayValues(a, message = f"VALUES AFTER {opts.episodes} EPISODES")
            display.pause()
        except KeyboardInterrupt:
            sys.exit(0)
