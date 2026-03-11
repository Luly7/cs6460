"""
Pacman agent implementations for Berkeley AI project.

This module provides different Pacman agent implementations including a left-turn
agent and a greedy agent. The agents demonstrate different movement strategies
and decision-making approaches in the Pacman environment.

Classes:
    LeftTurnAgent: Agent that prefers turning left when possible
    GreedyAgent: Agent that greedily selects highest-scoring moves

Functions:
    scoreEvaluation: Evaluates game state based on score

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added class and function descriptions
- Added Python version compatibility note
- Added modifier attribution
- Verified Python 3.13 compatibility
- Added type hints
- Updated to use f-strings

# pacmanAgents.py
# ---------------
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

from pacman import Directions
from game import Agent
import random
import game
import util
from typing import List, Tuple, Any, Callable


class LeftTurnAgent(game.Agent):
    """
    An agent that turns left at every opportunity.
    
    This agent implements a simple strategy of always trying to turn left when possible.
    If left turn is not available, it tries to continue straight, then right, then a full
    180-degree turn. Stops only as a last resort.
    """

    def getAction(self, state) -> str:
        """
        Determine next action prioritizing left turns.

        Args:
            state: Current game state

        Returns:
            str: Direction to move ('North', 'South', 'East', 'West', or 'Stop')
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
    """
    An agent that greedily selects moves maximizing immediate score.
    
    This agent evaluates each possible move based on the resulting game state's score
    and chooses randomly among moves tied for the highest score.
    """

    def __init__(self, evalFn: str="scoreEvaluation") -> None:
        """
        Initialize greedy agent with evaluation function.

        Args:
            evalFn: Name of evaluation function to use
        """
        self.evaluationFunction = util.lookup(evalFn, globals())
        assert self.evaluationFunction != None

    def getAction(self, state) -> str:
        """
        Choose action that maximizes immediate score.

        Args:
            state: Current game state

        Returns:
            str: Selected action direction
        """
        # Generate candidate actions
        legal = state.getLegalPacmanActions()
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        successors = [(state.generateSuccessor(0, action), action)
                      for action in legal]
        scored = [(self.evaluationFunction(state), action)
                  for state, action in successors]
        bestScore = max(scored)[0]
        bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
        return random.choice(bestActions)


def scoreEvaluation(state) -> float:
    """
    Evaluate game state based on score.

    Args:
        state: Game state to evaluate

    Returns:
        float: Current game score
    """
    return state.getScore()
