
"""
Feature extractors for Pacman game states.

This module provides feature extractors that convert game states into feature vectors
for use in reinforcement learning and machine learning algorithms. The extractors
transform raw game states into meaningful numeric features that capture important
aspects of the game state. Key extractors include:

- IdentityExtractor: Basic state-action pair features for direct state representation
- CoordinateExtractor: Position and action based features for spatial reasoning
- SimpleExtractor: Basic reflex features like food and ghost distances for reactive behavior

Features are returned as Counter objects mapping feature names to numeric values.
The features can be used to train reinforcement learning agents or other ML models.

Most code originally by Dan Klein and John Denero for CS188 at UC Berkeley.
Some code from LiveWires Pacman implementation, used with permission.

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added detailed feature extractor descriptions
- Added type hints throughout module
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

from game import Directions, Actions
import util
from typing import Dict, List, Tuple, Any, Optional

class FeatureExtractor:
    def getFeatures(self, state: Any, action: str) -> util.Counter:
        """
        Returns a dict mapping features to their values.
        
        Args:
            state: Current game state
            action: Proposed action
            
        Returns:
            Counter mapping feature names to numeric values, typically 1.0 for
            indicator functions
        """
        util.raiseNotDefined()

class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state: Any, action: str) -> util.Counter:
        """
        Returns simple state-action pair feature.
        
        Args:
            state: Current game state
            action: Proposed action
            
        Returns:
            Counter with single (state,action) feature
        """
        feats = util.Counter()
        feats[(state,action)] = 1.0
        return feats

class CoordinateExtractor(FeatureExtractor):
    def getFeatures(self, state: Any, action: str) -> util.Counter:
        """
        Returns features based on coordinates and action.
        
        Args:
            state: Current game state coordinates
            action: Proposed action
            
        Returns:
            Counter with state coordinates and action features
        """
        feats = util.Counter()
        feats[state] = 1.0
        feats[f'x={state[0]}'] = 1.0
        feats[f'y={state[0]}'] = 1.0
        feats[f'action={action}'] = 1.0
        return feats

def closestFood(pos: Tuple[int, int], food: List[List[bool]], walls: List[List[bool]]) -> Optional[int]:
    """
    Finds distance to closest food using BFS search.
    
    Args:
        pos: (x,y) starting position
        food: 2D boolean array indicating food locations
        walls: 2D boolean array indicating wall locations
        
    Returns:
        Distance to closest food, or None if no food found
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a food at this location then exit
        if food[pos_x][pos_y]:
            return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no food found
    return None

class SimpleExtractor(FeatureExtractor):
    """
    Returns simple features for a basic reflex Pacman.
    
    Features extracted:
    - bias: Constant 1.0 feature
    - #-of-ghosts-1-step-away: Count of nearby ghosts
    - eats-food: Whether action leads to food
    - closest-food: Distance to nearest food (normalized)
    """

    def getFeatures(self, state: Any, action: str) -> util.Counter:
        """
        Extract basic movement features from state.
        
        Args:
            state: Current game state
            action: Proposed action
            
        Returns:
            Counter with extracted feature values, normalized by 10.0
        """
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()

        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # count the number of ghosts 1-step away
        features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

        # if there is no danger of ghosts then add the food feature
        if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)
        features.divideAll(10.0)
        return features
