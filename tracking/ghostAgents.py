"""
ghostAgents.py
-------------
This module implements various ghost agents for the Pacman game, including random
and directional ghosts that either chase or flee from Pacman.

The ghosts use different strategies to move through the maze, from completely random
movement to more sophisticated path planning and behavior patterns.

Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).

Modified 19 Dec 2024 by George Rudolph:
- Verified compatibility with Python 3.13
- Added comprehensive module docstring
- Improved type hints and documentation
- Enhanced code organization and readability
"""


from game import Agent, Actions, Directions
from typing import Dict, List, Tuple
import random
from util import manhattanDistance
import util


class GhostAgent(Agent):
    def __init__(self, index: int) -> None:
        self.index = index

    def getAction(self, state) -> str:
        dist = self.getDistribution(state)
        if len(dist) == 0:
            return Directions.STOP
        else:
            return util.chooseFromDistribution(dist)

    def getDistribution(self, state) -> util.Counter:
        """Returns a Counter encoding a distribution over actions from the provided state."""
        util.raiseNotDefined()


class RandomGhost(GhostAgent):
    """A ghost that chooses a legal action uniformly at random."""

    def getDistribution(self, state) -> util.Counter:
        dist = util.Counter()
        for a in state.getLegalActions(self.index):
            dist[a] = 1.0
        dist.normalize()
        return dist


class DirectionalGhost(GhostAgent):
    """A ghost that prefers to rush Pacman, or flee when scared."""

    def __init__(self, index: int, prob_attack: float = 0.8, prob_scaredFlee: float = 0.8) -> None:
        self.index = index
        self.prob_attack = prob_attack
        self.prob_scaredFlee = prob_scaredFlee

    def getDistribution(self, state) -> util.Counter:
        # Read variables from state
        ghostState = state.getGhostState(self.index)
        legalActions = state.getLegalActions(self.index)
        pos = state.getGhostPosition(self.index)
        isScared = ghostState.scaredTimer > 0

        speed = 1
        if isScared:
            speed = 0.5

        actionVectors = [Actions.directionToVector(a, speed) for a in legalActions]
        newPositions = [(pos[0] + a[0], pos[1] + a[1]) for a in actionVectors]
        pacmanPosition = state.getPacmanPosition()

        # Select best actions given the state
        distancesToPacman = [
            manhattanDistance(pos, pacmanPosition) for pos in newPositions
        ]
        if isScared:
            bestScore = max(distancesToPacman)
            bestProb = self.prob_scaredFlee
        else:
            bestScore = min(distancesToPacman)
            bestProb = self.prob_attack
        bestActions = [
            action
            for action, distance in zip(legalActions, distancesToPacman)
            if distance == bestScore
        ]

        # Construct distribution
        dist = util.Counter()
        for a in bestActions:
            dist[a] = bestProb / len(bestActions)
        for a in legalActions:
            dist[a] += (1 - bestProb) / len(legalActions)
        dist.normalize()
        return dist
