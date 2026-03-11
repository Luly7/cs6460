"""Pacman agent implementations for the Berkeley AI projects.

This module provides different Pacman agent implementations with varying strategies,
from simple rule-based agents like LeftTurnAgent to more sophisticated agents like
GreedyAgent that use evaluation functions to select actions.

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


from pacman import Directions
from game import Agent
import random
import game
import util
from typing import List


class LeftTurnAgent(game.Agent):
    """An agent that turns left at every opportunity.
    
    This agent implements a simple strategy of always trying to turn left when possible.
    If a left turn is not available, it tries to continue straight, then right, then a
    full reversal, falling back to stopping only if no other moves are legal.
    """

    def getAction(self, state) -> str:
        """Choose the next action for the agent based on legal moves.
        
        Args:
            state: Current game state
            
        Returns:
            str: Direction to move (from Directions constants)
        """
        legal: List[str] = state.getLegalPacmanActions()
        current: str = state.getPacmanState().configuration.direction
        if current == Directions.STOP:
            current = Directions.NORTH
        left: str = Directions.LEFT[current]
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
    """A greedy agent that selects actions based on state evaluation scores.
    
    This agent evaluates possible successor states using a provided evaluation function
    and greedily chooses actions that lead to states with the highest scores.
    
    Attributes:
        evaluationFunction: Function that takes a state and returns a numeric score
    """
    
    def __init__(self, evalFn: str = "scoreEvaluation") -> None:
        """Initialize the greedy agent with an evaluation function.
        
        Args:
            evalFn: Name of the evaluation function to use (default: "scoreEvaluation")
        """
        self.evaluationFunction = util.lookup(evalFn, globals())
        assert self.evaluationFunction is not None

    def getAction(self, state) -> str:
        """Choose the next action that leads to the highest-scoring successor state.
        
        Args:
            state: Current game state
            
        Returns:
            str: The selected action direction
        """
        # Generate candidate actions
        legal: List[str] = state.getLegalPacmanActions()
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
    """Simple evaluation function that returns the game score.
    
    Args:
        state: Game state to evaluate
        
    Returns:
        float: The game score for the given state
    """
    return state.getScore()
