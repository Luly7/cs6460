"""
Learning agents for reinforcement learning in Pacman.

This module provides base classes for reinforcement learning agents that estimate
values and learn from experience in the Pacman environment. The key classes are:

- ValueEstimationAgent: Abstract base class for agents that estimate state-action 
  values using methods like value iteration or Q-learning. Maintains Q-values and
  derives optimal policies.

- ReinforcementAgent: Abstract base class for agents that learn from experience
  through episodes. Handles training/testing phases, reward tracking, and 
  exploration vs exploitation.

The base classes implement common functionality like episode management and 
parameter tracking, while specific learning algorithms are implemented in child
classes like QLearningAgent.

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added type hints  
- Added detailed class descriptions
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

import random
import time
import util
from game import Directions, Agent, Actions
from typing import List, Dict, Optional, Callable, Any, Union, Tuple



class ValueEstimationAgent(Agent):
    """
    Abstract agent which assigns values to (state,action) pairs.
    
    Maintains Q-Values for state-action pairs and derives state values and policies:
    V(s) = max_{a in actions} Q(s,a)
    policy(s) = arg_max_{a in actions} Q(s,a)
    
    Parent class for both ValueIterationAgent (model-based) and 
    QLearningAgent (model-free) implementations.
    """

    def __init__(self, alpha: float = 1.0, epsilon: float = 0.05, 
                 gamma: float = 0.8, numTraining: int = 10) -> None:
        """
        Initialize learning parameters.

        Args:
            alpha: Learning rate for value updates
            epsilon: Exploration rate for action selection
            gamma: Discount factor for future rewards
            numTraining: Number of training episodes before testing
        """
        self.alpha = float(alpha)
        self.epsilon = float(epsilon)
        self.discount = float(gamma)
        self.numTraining = int(numTraining)

    ####################################
    #    Override These Functions      #
    ####################################
    def getQValue(self, state: Any, action: Any) -> float:
        """
        Get Q-value for state-action pair.

        Args:
            state: Current game state
            action: Proposed action
            
        Returns:
            Estimated Q-value Q(state,action)
        """
        util.raiseNotDefined()

    def getValue(self, state: Any) -> float:
        """
        Get maximum Q-value for state under any action.
        
        Computes V(s) = max_{a in actions} Q(s,a)

        Args:
            state: Current game state
            
        Returns:
            Maximum Q-value achievable from state
        """
        util.raiseNotDefined()

    def getPolicy(self, state: Any) -> Any:
        """
        Get best action for state according to Q-values.
        
        Computes policy(s) = arg_max_{a in actions} Q(s,a)
        If multiple actions achieve max Q-value, any may be returned.

        Args:
            state: Current game state
            
        Returns:
            Action achieving maximum Q-value
        """
        util.raiseNotDefined()

    def getAction(self, state: Any) -> Any:
        """
        Choose action to take in current state.
        
        May differ from policy for exploration purposes.

        Args:
            state: Current game state that has getLegalActions() method
            
        Returns:
            Selected action to take
        """
        util.raiseNotDefined()

class ReinforcementAgent(ValueEstimationAgent):
    """
    Abstract reinforcement learning agent that learns from experience.
    
    Learns Q-values through environment interaction rather than a model.
    Handles episode management, reward accumulation, and training/testing phases.
    
    Key methods to implement:
    - update(state, action, nextState, deltaReward): Update Q-values from transition
    - getLegalActions(state): Get available actions in state
    """
    ####################################
    #    Override These Functions      #
    ####################################

    def update(self, state: Any, action: Any, nextState: Any, reward: float) -> None:
        """
        Update agent's knowledge after observing transition.
        
        Called after each (state,action,nextState,reward) transition.

        Args:
            state: Starting state
            action: Action taken
            nextState: Resulting state
            reward: Reward received
        """
        util.raiseNotDefined()

    ####################################
    #    Read These Functions          #
    ####################################

    def getLegalActions(self, state: Any) -> List[Any]:
        """
        Get legal actions available in given state.
        
        Args:
            state: Current game state
            
        Returns:
            List of legal actions in state
        """
        return self.actionFn(state)

    def observeTransition(self, state: Any, action: Any, 
                         nextState: Any, deltaReward: float) -> None:
        """
        Process observed transition and update agent accordingly.
        
        Accumulates episode rewards and calls update().
        
        Args:
            state: Starting state
            action: Action taken  
            nextState: Resulting state
            deltaReward: Reward received
            
        Note: Do not override or call this function directly
        """
        self.episodeRewards += deltaReward
        self.update(state,action,nextState,deltaReward)

    def startEpisode(self) -> None:
        """Initialize state for new episode."""
        self.lastState = None
        self.lastAction = None
        self.episodeRewards = 0.0

    def stopEpisode(self) -> None:
        """
        Clean up after episode completion.
        
        Accumulates rewards and updates learning parameters if training complete.
        """
        if self.episodesSoFar < self.numTraining:
            self.accumTrainRewards += self.episodeRewards
        else:
            self.accumTestRewards += self.episodeRewards
        self.episodesSoFar += 1
        if self.episodesSoFar >= self.numTraining:
            # Take off the training wheels
            self.epsilon = 0.0    # no exploration
            self.alpha = 0.0      # no learning

    def isInTraining(self) -> bool:
        """Check if agent is still in training phase."""
        return self.episodesSoFar < self.numTraining

    def isInTesting(self) -> bool:
        """Check if agent is in testing phase."""
        return not self.isInTraining()

    def __init__(self, actionFn: Optional[Callable] = None, numTraining: int = 100, 
                 epsilon: float = 0.5, alpha: float = 0.5, gamma: float = 1) -> None:
        """
        Initialize reinforcement learning agent.

        Args:
            actionFn: Function that takes state and returns legal actions
            numTraining: Number of training episodes
            epsilon: Exploration rate
            alpha: Learning rate
            gamma: Discount factor
        """
        if actionFn == None:
            actionFn = lambda state: state.getLegalActions()
        self.actionFn = actionFn
        self.episodesSoFar = 0
        self.accumTrainRewards = 0.0
        self.accumTestRewards = 0.0
        self.numTraining = int(numTraining)
        self.epsilon = float(epsilon)
        self.alpha = float(alpha)
        self.discount = float(gamma)

    ################################
    # Controls needed for Crawler  #
    ################################
    def setEpsilon(self, epsilon: float) -> None:
        """Set exploration rate."""
        self.epsilon = epsilon

    def setLearningRate(self, alpha: float) -> None:
        """Set learning rate."""
        self.alpha = alpha

    def setDiscount(self, discount: float) -> None:
        """Set discount factor."""
        self.discount = discount

    def doAction(self, state: Any, action: Any) -> None:
        """
        Record last state and action.
        
        Called by child classes when taking actions.

        Args:
            state: Current state
            action: Action being taken
        """
        self.lastState = state
        self.lastAction = action

    ###################
    # Pacman Specific #
    ###################
    def observationFunction(self, state: Any) -> Any:
        """
        Process new state observation after last action.
        
        Args:
            state: New game state
            
        Returns:
            The observed state
        """
        if not self.lastState is None:
            reward = state.getScore() - self.lastState.getScore()
            self.observeTransition(self.lastState, self.lastAction, state, reward)
        return state

    def registerInitialState(self, state: Any) -> None:
        """
        Initialize episode and print training message if first episode.
        
        Args:
            state: Initial game state
        """
        self.startEpisode()
        if self.episodesSoFar == 0:
            print(f'Beginning {self.numTraining} episodes of Training')

    def final(self, state: Any) -> None:
        """
        Handle end of episode.
        
        Updates Q-values for final transition and prints progress statistics.

        Args:
            state: Terminal game state
        """
        deltaReward = state.getScore() - self.lastState.getScore()
        self.observeTransition(self.lastState, self.lastAction, state, deltaReward)
        self.stopEpisode()

        # Make sure we have this var
        if not 'episodeStartTime' in self.__dict__:
            self.episodeStartTime = time.time()
        if not 'lastWindowAccumRewards' in self.__dict__:
            self.lastWindowAccumRewards = 0.0
        self.lastWindowAccumRewards += state.getScore()

        NUM_EPS_UPDATE = 100
        if self.episodesSoFar % NUM_EPS_UPDATE == 0:
            print('Reinforcement Learning Status:')
            windowAvg = self.lastWindowAccumRewards / float(NUM_EPS_UPDATE)
            if self.episodesSoFar <= self.numTraining:
                trainAvg = self.accumTrainRewards / float(self.episodesSoFar)
                print(f'\tCompleted {self.episodesSoFar} out of {self.numTraining} training episodes')
                print(f'\tAverage Rewards over all training: {trainAvg:.2f}')
            else:
                testAvg = float(self.accumTestRewards) / (self.episodesSoFar - self.numTraining)
                print(f'\tCompleted {self.episodesSoFar - self.numTraining} test episodes')
                print(f'\tAverage Rewards over testing: {testAvg:.2f}')
            print(f'\tAverage Rewards for last {NUM_EPS_UPDATE} episodes: {windowAvg:.2f}')
            print(f'\tEpisode took {time.time() - self.episodeStartTime:.2f} seconds')
            self.lastWindowAccumRewards = 0.0
            self.episodeStartTime = time.time()

        if self.episodesSoFar == self.numTraining:
            msg = 'Training Done (turning off epsilon and alpha)'
            print(f'{msg}\n{"-" * len(msg)}')
