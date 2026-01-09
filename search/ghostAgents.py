"""Ghost agent implementations for Pacman game.

This module provides ghost agent classes that define different ghost behaviors
in the Pacman game, including random ghosts and directional ghosts.

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
    - Added comprehensive docstrings
    - Added type hints throughout
    - Improved code organization
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


from game import Agent
from game import Actions
from game import Directions
from pacman import GameState
import random
from util import manhattanDistance
import util
from typing import List, Tuple, Dict

class GhostAgent(Agent):
    """Base class for ghost agents."""
    
    def __init__(self, index: int) -> None:
        """
        Initialize ghost agent.
        
        Args:
            index: Index of this ghost agent
        """
        self.index = index

    def getAction(self, state: GameState) -> str:
        """
        Get an action from the distribution.
        
        Args:
            state: Current game state
            
        Returns:
            Direction to move in
        """
        dist = self.getDistribution(state)
        if len(dist) == 0:
            return Directions.STOP
        else:
            return util.chooseFromDistribution(dist)

    def getDistribution(self, state: GameState) -> util.Counter:
        """
        Returns a Counter encoding a distribution over actions from the provided state.
        
        Args:
            state: Current game state
            
        Returns:
            Counter with probabilities for each action
        """
        util.raiseNotDefined()

class RandomGhost(GhostAgent):
    """A ghost that chooses a legal action uniformly at random."""
    
    def getDistribution(self, state: GameState) -> util.Counter:
        """
        Get uniform random distribution over legal actions.
        
        Args:
            state: Current game state
            
        Returns:
            Counter with equal probabilities for each legal action
        """
        dist = util.Counter()
        for a in state.getLegalActions(self.index):
            dist[a] = 1.0
        dist.normalize()
        return dist

class DirectionalGhost(GhostAgent):
    """A ghost that prefers to rush Pacman, or flee when scared."""
    
    def __init__(self, index: int, prob_attack: float = 0.8, prob_scaredFlee: float = 0.8) -> None:
        """
        Initialize directional ghost.
        
        Args:
            index: Index of this ghost
            prob_attack: Probability of moving toward Pacman when not scared
            prob_scaredFlee: Probability of moving away from Pacman when scared
        """
        self.index = index
        self.prob_attack = prob_attack
        self.prob_scaredFlee = prob_scaredFlee

    def getDistribution(self, state: GameState) -> util.Counter:
        """
        Get distribution favoring moving toward/away from Pacman.
        
        Args:
            state: Current game state
            
        Returns:
            Counter with action probabilities based on Pacman's position
        """
        # Read variables from state
        ghostState = state.getGhostState(self.index)
        legalActions = state.getLegalActions(self.index)
        pos = state.getGhostPosition(self.index)
        isScared = ghostState.scaredTimer > 0

        speed = 0.5 if isScared else 1

        actionVectors = [Actions.directionToVector(a, speed) for a in legalActions]
        newPositions = [(pos[0] + a[0], pos[1] + a[1]) for a in actionVectors]
        pacmanPosition = state.getPacmanPosition()

        # Select best actions given the state
        distancesToPacman = [manhattanDistance(pos, pacmanPosition) for pos in newPositions]
        if isScared:
            bestScore = max(distancesToPacman)
            bestProb = self.prob_scaredFlee
        else:
            bestScore = min(distancesToPacman)
            bestProb = self.prob_attack
        bestActions = [action for action, distance in zip(legalActions, distancesToPacman) if distance == bestScore]

        # Construct distribution
        dist = util.Counter()
        for a in bestActions:
            dist[a] = bestProb / len(bestActions)
        for a in legalActions:
            dist[a] += (1-bestProb) / len(legalActions)
        dist.normalize()
        return dist
