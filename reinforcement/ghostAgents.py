"""
Ghost agents for Pacman game.

This module provides ghost agent implementations for the Pacman game. It includes:
- Base GhostAgent class defining core ghost behavior
- RandomGhost that moves randomly
- DirectionalGhost that prefers certain directions
- Scared ghost behavior when Pacman has power pellets

The ghosts use probability distributions to select actions and can be:
- Configured with different movement strategies
- Made to behave differently when scared
- Given different personalities through weights
- Made to work in both classic and capture modes

Most code originally by Dan Klein and John Denero for CS188 at UC Berkeley.
Some code from LiveWires Pacman implementation, used with permission.

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added type hints throughout module
- Added detailed ghost configuration options
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


from game import Agent
from game import Actions
from game import Directions
import random
from util import manhattanDistance
import util
from typing import List, Dict, Tuple, Any, Optional


class GhostAgent(Agent):
    """Base class for ghost agents in Pacman.
    
    Provides core functionality for ghost behavior including action selection
    based on probability distributions.
    """
    
    def __init__(self, index: int) -> None:
        """Initialize ghost agent with index.
        
        Args:
            index: Integer index identifying this ghost
        """
        self.index = index

    def getAction(self, state: Any) -> str:
        """Get an action from the ghost's probability distribution.
        
        Args:
            state: Current game state
            
        Returns:
            Direction string for chosen action
        """
        dist = self.getDistribution(state)
        if len(dist) == 0:
            return Directions.STOP
        else:
            return util.chooseFromDistribution(dist)

    def getDistribution(self, state: Any) -> util.Counter:
        """Get probability distribution over actions for current state.
        
        Args:
            state: Current game state
            
        Returns:
            Counter mapping actions to probabilities
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        util.raiseNotDefined()


class RandomGhost(GhostAgent):
    """Ghost agent that chooses legal actions uniformly at random."""

    def getDistribution(self, state: Any) -> util.Counter:
        """Get uniform distribution over legal actions.
        
        Args:
            state: Current game state
            
        Returns:
            Counter with equal probabilities for all legal actions
        """
        dist = util.Counter()
        for a in state.getLegalActions(self.index):
            dist[a] = 1.0
        dist.normalize()
        return dist


class DirectionalGhost(GhostAgent):
    """Ghost agent that rushes toward Pacman or flees when scared."""

    def __init__(self, index: int, prob_attack: float = 0.8, prob_scaredFlee: float = 0.8) -> None:
        """Initialize directional ghost parameters.
        
        Args:
            index: Integer index identifying this ghost
            prob_attack: Probability of moving toward Pacman when not scared
            prob_scaredFlee: Probability of fleeing from Pacman when scared
        """
        self.index = index
        self.prob_attack = prob_attack
        self.prob_scaredFlee = prob_scaredFlee

    def getDistribution(self, state: Any) -> util.Counter:
        """Get action distribution based on Pacman distance and scared state.
        
        Args:
            state: Current game state
            
        Returns:
            Counter mapping actions to probabilities based on Pacman position
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
