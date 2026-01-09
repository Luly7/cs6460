"""Pacman agents implementing various movement strategies.

This module contains different Pacman agent implementations that control Pacman's
movement through the maze using different strategies like turning left, greedy
evaluation, etc.

Original Authors:
    John DeNero (denero@cs.berkeley.edu)
    Dan Klein (klein@cs.berkeley.edu)
    Brad Miller
    Nick Hay
    Pieter Abbeel (pabbeel@cs.berkeley.edu)

Modified by:
    George Rudolph
    Date: 9 Nov 2024

Changes:
    - Added type hints
    - Improved docstrings and documentation
    - Verified to run with Python 3.13

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

from pacman import Directions, GameState
from game import Agent
import random
import game
import util

class LeftTurnAgent(game.Agent):
    """An agent that turns left at every opportunity.
    
    This agent follows a simple strategy of always trying to turn left when possible.
    If it cannot turn left, it tries to continue straight, then right, then a full 180
    degree turn. If no moves are possible, it stops.
    
    Attributes:
        None
    """

    def getAction(self, state: GameState) -> str:
        """Determines the next action for the agent based on the game state.
        
        Args:
            state: A GameState object representing the current game state
            
        Returns:
            str: The chosen direction to move (one of the Directions constants)
        """
        legal = state.getLegalPacmanActions()
        current = state.getPacmanState().configuration.direction
        if current == Directions.STOP:
            current = Directions.NORTH
        left = Directions.LEFT[current]
        
        if left in legal:
            return left
        if current in legal:
            return current
        if Directions.RIGHT[current] in legal:
            return Directions.RIGHT[current]
        if Directions.LEFT[left] in legal:
            return Directions.LEFT[left]
        return Directions.STOP

class GreedyAgent(Agent):
    """A greedy agent that selects actions based on a provided evaluation function.
    
    This agent evaluates possible successor states using an evaluation function and
    chooses the action that leads to the highest scoring state. If multiple actions
    tie for the best score, one is chosen randomly.
    
    Attributes:
        evaluationFunction (Callable[[game.GameState], float]): Function used to score states
    """
    
    def __init__(self, evalFn: str = "scoreEvaluation") -> None:
        """Initialize the greedy agent with an evaluation function.
        
        Args:
            evalFn: Name of the evaluation function to use, defaults to "scoreEvaluation"
        """
        self.evaluationFunction = util.lookup(evalFn, globals())
        assert self.evaluationFunction is not None

    def getAction(self, state: GameState) -> str:
        """Choose the best action based on evaluating successor states.
        
        Args:
            state: Current game state
            
        Returns:
            str: The chosen direction to move (one of the Directions constants)
        """
        # Generate candidate actions
        legal = state.getLegalPacmanActions()
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        successors = [(state.generateSuccessor(0, action), action) for action in legal]
        scored = [(self.evaluationFunction(state), action) for state, action in successors]
        bestScore = max(scored)[0]
        bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
        return random.choice(bestActions)

def scoreEvaluation(state: GameState) -> float:
    """Evaluate a game state by returning its current score.
    
    Args:
        state: The game state to evaluate
        
    Returns:
        float: The score of the given state
    """
    return state.getScore()
