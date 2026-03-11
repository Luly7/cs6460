"""
Q-learning agents for reinforcement learning in Pacman.

This module implements Q-learning agents that learn optimal policies through
experience in the Pacman environment. It includes tabular Q-learning and
approximate Q-learning with feature-based representations. The agents use
epsilon-greedy exploration and temporal difference learning to update Q-values.

Classes:
    QLearningAgent: Base tabular Q-learning implementation
    PacmanQAgent: Q-learning agent adapted for Pacman
    ApproximateQAgent: Q-learning with feature approximation

Functions:
    None

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added type hints
- Added class descriptions
- Added function section to docstring
- Verified Python 3.13 compatibility
- Added modifier attribution

# qlearningAgents.py
# ------------------
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
from typing import Any, Dict, List, Optional, Tuple, Union

import math
import random
import util

from game import *
from learningAgents import ReinforcementAgent
from featureExtractors import *



class QLearningAgent(ReinforcementAgent):
    """
    Q-Learning Agent that learns through experience.

    This agent implements the Q-learning algorithm to learn optimal action values
    through exploration and exploitation. It maintains Q-values for state-action pairs
    and updates them based on received rewards and future value estimates.

    Key Functions:
        - computeValueFromQValues: Computes maximum Q-value for a state
        - computeActionFromQValues: Determines best action based on Q-values
        - getQValue: Retrieves Q-value for a state-action pair
        - getAction: Selects action using epsilon-greedy policy
        - update: Updates Q-values based on experience

    Instance Variables:
        - self.epsilon: Exploration probability
        - self.alpha: Learning rate
        - self.discount: Discount factor for future rewards
    """
    def __init__(self, **args) -> None:
        """Initialize Q-learning agent with empty Q-value table."""
        ReinforcementAgent.__init__(self, **args)

        "*** YOUR CODE HERE ***"


    def getQValue(self, state: Any, action: Any) -> float:
        """
        Get Q-value for a state-action pair.

        Args:
            state: Current game state
            action: Action to evaluate

        Returns:
            float: Q-value for the state-action pair, 0.0 if never seen
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

    def computeValueFromQValues(self, state: Any) -> float:
        """
        Compute maximum Q-value over all legal actions for a state.

        Args:
            state: Current game state

        Returns:
            float: Maximum Q-value, 0.0 if no legal actions exist
        """
        "*** YOUR CODE HERE ***"

        util.raiseNotDefined()

    def computeActionFromQValues(self, state: Any) -> Any:
        """
        Compute optimal action to take in a state based on Q-values.

        Args:
            state: Current game state

        Returns:
            Action: Best action to take, None if no legal actions exist
        """
        "*** YOUR CODE HERE ***"

        util.raiseNotDefined()


    def getAction(self, state: Any) -> Any:
        """
        Select action using epsilon-greedy policy.

        With probability epsilon, chooses a random action for exploration.
        Otherwise, chooses the best action based on current Q-values.

        Args:
            state: Current game state

        Returns:
            Action: Selected action, None if no legal actions exist
        """
        # Pick Action
        actions = self.getLegalActions(state)
        action = None
        "*** YOUR CODE HERE ***"

        util.raiseNotDefined()

    def update(self, state: Any, action: Any, s_prime: Any, reward: float) -> None:
        """
        Update Q-values based on observed transition.

        Performs Q-learning update using the formula:
        Q(s,a) = (1-α)Q(s,a) + α[r + γ*max_a'Q(s',a')]

        Args:
            state: Starting state
            action: Action taken
            s_prime: Resulting next state
            reward: Reward received
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

    def getPolicy(self, state: Any) -> Any:
        return self.computeActionFromQValues(state)

    def getValue(self, state: Any) -> float:
        return self.computeValueFromQValues(state)


class PacmanQAgent(QLearningAgent):
    """Q-Learning agent adapted for Pacman with modified default parameters."""

    def __init__(self, epsilon: float=0.05, gamma: float=0.8, alpha: float=0.2, numTraining: int=0, **args) -> None:
        """
        Initialize PacmanQAgent with specific default parameters.

        Args:
            epsilon: Exploration rate
            gamma: Discount factor
            alpha: Learning rate
            numTraining: Number of training episodes
            **args: Additional arguments
        """
        args['epsilon'] = epsilon
        args['gamma'] = gamma
        args['alpha'] = alpha
        args['numTraining'] = numTraining
        self.index = 0  # This is always Pacman
        QLearningAgent.__init__(self, **args)

    def getAction(self, state: Any) -> Any:
        """
        Get action from Q-learning agent and inform parent.

        Args:
            state: Current game state

        Returns:
            Action: Selected action
        """
        action = QLearningAgent.getAction(self,state)
        self.doAction(state,action)
        return action


class ApproximateQAgent(PacmanQAgent):
    """
    Approximate Q-Learning agent using feature-based representation.

    This agent uses linear function approximation to estimate Q-values,
    representing them as a weighted sum of features. Only getQValue
    and update methods need to be modified from the base QLearningAgent.
    """
    def __init__(self, extractor: str='IdentityExtractor', **args) -> None:
        self.featExtractor = util.lookup(extractor, globals())()
        PacmanQAgent.__init__(self, **args)
        self.weights = util.Counter()

    def getWeights(self) -> util.Counter:
        return self.weights

    def getQValue(self, state: Any, action: Any) -> float:
        """
        Compute Q-value as dot product of weights and features.

        Args:
            state: Current game state
            action: Action to evaluate

        Returns:
            float: Approximated Q-value
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

    def update(self, state: Any, action: Any, nextState: Any, reward: float) -> None:
        """
        Update feature weights based on transition.

        Args:
            state: Starting state
            action: Action taken
            nextState: Resulting state
            reward: Reward received
        """
        "*** YOUR CODE HERE ***"

        util.raiseNotDefined()

    def final(self, state: Any) -> None:
        """
        Called at the end of each game.

        Args:
            state: Final game state
        """
        # call the super-class final method
        PacmanQAgent.final(self, state)

        # did we finish training?
        if self.episodesSoFar == self.numTraining:
            # you might want to print your weights here for debugging
            "*** YOUR CODE HERE ***"
            pass
