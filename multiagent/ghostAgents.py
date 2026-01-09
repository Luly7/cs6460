"""Ghost agents module for Pacman game.

This module provides ghost agent implementations for the Pacman game, including
base ghost behavior and specific ghost types like random ghosts.

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


from game import Agent
from game import Actions
from game import Directions
import random
from util import manhattanDistance
import util

class GhostAgent(Agent):
    """Base class for ghost agents in Pacman.
    
    Attributes:
        index: Integer index identifying which ghost this agent controls
    """
    def __init__(self, index: int) -> None:
        self.index = index

    def getAction(self, state: 'GameState') -> str:
        """Get the ghost's next action based on the state.
        
        Args:
            state: Current game state
            
        Returns:
            Direction string indicating ghost's next move
        """
        dist = self.getDistribution(state)
        if len(dist) == 0:
            return Directions.STOP
        else:
            return util.chooseFromDistribution(dist)

    def getDistribution(self, state: 'GameState') -> 'Counter':
        """Get probability distribution over actions from the current state.
        
        Args:
            state: Current game state
            
        Returns:
            Counter mapping actions to probabilities
            
        Raises:
            NotImplementedError: This is an abstract method that should be overridden
        """
        util.raiseNotDefined()


class RandomGhost(GhostAgent):
    """A ghost that chooses a legal action uniformly at random."""

    def getDistribution(self, state: 'GameState') -> 'Counter':
        """Get uniform random distribution over legal actions.
        
        Args:
            state: Current game state
            
        Returns:
            Counter mapping each legal action to equal probability
        """
        dist = util.Counter()
        for a in state.getLegalActions(self.index):
            dist[a] = 1.0
        dist.normalize()
        return dist


class DirectionalGhost(GhostAgent):
    """A ghost that prefers to rush Pacman, or flee when scared.
    
    This ghost will aggressively chase Pacman when not scared, and run away when scared.
    The ghost's behavior is controlled by probability parameters that determine how likely
    it is to choose optimal actions versus random movement.
    
    Attributes:
        index: Ghost's index number
        prob_attack: Probability of choosing optimal attack action when not scared
        prob_scaredFlee: Probability of choosing optimal flee action when scared
    """

    def __init__(self, index: int, prob_attack: float = 0.8, prob_scaredFlee: float = 0.8) -> None:
        """Initialize ghost parameters.
        
        Args:
            index: Ghost's index number
            prob_attack: Probability of choosing optimal attack action when not scared
            prob_scaredFlee: Probability of choosing optimal flee action when scared
        """
        self.index = index
        self.prob_attack = prob_attack
        self.prob_scaredFlee = prob_scaredFlee

    def getDistribution(self, state: 'GameState') -> 'Counter':
        """Get probability distribution over actions from current state.
        
        Args:
            state: Current game state
            
        Returns:
            Counter mapping actions to probabilities
        """
        # Read variables from state
        ghostState = state.getGhostState(self.index)
        legalActions = state.getLegalActions(self.index)
        pos = state.getGhostPosition(self.index)
        isScared = ghostState.scaredTimer > 0

        speed = 1
        if isScared:
            speed = 0.5

        actionVectors = [Actions.directionToVector(
            a, speed) for a in legalActions]
        newPositions = [(pos[0]+a[0], pos[1]+a[1]) for a in actionVectors]
        pacmanPosition = state.getPacmanPosition()

        # Select best actions given the state
        distancesToPacman = [manhattanDistance(
            pos, pacmanPosition) for pos in newPositions]
        if isScared:
            bestScore = max(distancesToPacman)
            bestProb = self.prob_scaredFlee
        else:
            bestScore = min(distancesToPacman)
            bestProb = self.prob_attack
        bestActions = [action for action, distance in zip(
            legalActions, distancesToPacman) if distance == bestScore]

        # Construct distribution
        dist = util.Counter()
        for a in bestActions:
            dist[a] = bestProb / len(bestActions)
        for a in legalActions:
            dist[a] += (1-bestProb) / len(legalActions)
        dist.normalize()
        return dist
