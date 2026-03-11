"""
Markov Decision Process (MDP) abstract base class.

This module defines the core interface for Markov Decision Process environments.
An MDP consists of:
- States: The possible configurations of the environment
- Actions: What can be done in each state 
- Transitions: How actions change the state (with probabilities)
- Rewards: Numeric feedback for state-action-state transitions

The MDP interface is used by reinforcement learning and planning algorithms
to interact with environments in a standard way.

Python Version: 3.13
Last Modified: 27 Feb 2022
Modified by: George Rudolph

Changes:
- Added abc module and abstract method decorators
- Added comprehensive docstrings and type hints

# mdp.py
# ------
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

import abc
from typing import List, Tuple, Any

class MarkovDecisionProcess(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def getStates(self) -> List[Any]:
        """
        Return a list of all states in the MDP.
        
        Note: Not generally feasible for large MDPs.
        
        Returns:
            List of all possible states in the environment
        """
        return

    @abc.abstractmethod
    def getStartState(self) -> Any:
        """
        Return the initial state of the MDP.
        
        Returns:
            The state where the agent begins
        """
        return

    @abc.abstractmethod
    def getPossibleActions(self, state: Any) -> List[Any]:
        """
        Return list of possible actions available in given state.
        
        Args:
            state: The current state
            
        Returns:
            List of actions that can be taken from this state
        """
        return

    @abc.abstractmethod
    def getTransitionStatesAndProbs(self, state: Any, action: Any) -> List[Tuple[Any, float]]:
        """
        Get the transition model for a state-action pair.
        
        Args:
            state: The current state
            action: The action to take
            
        Returns:
            List of (nextState, probability) pairs representing possible
            next states and their transition probabilities
            
        Note:
            In Q-Learning and reinforcement learning generally, these
            probabilities are not known or directly modeled.
        """
        return

    @abc.abstractmethod
    def getReward(self, state: Any, action: Any, nextState: Any) -> float:
        """
        Get the reward for a state-action-nextState transition.
        
        Args:
            state: The current state
            action: The action taken
            nextState: The resulting next state
            
        Returns:
            The reward value for this transition
            
        Note:
            Not typically available in reinforcement learning settings.
        """
        return
        
    @abc.abstractmethod
    def isTerminal(self, state: Any) -> bool:
        """
        Check if a state is terminal.
        
        Args:
            state: The state to check
            
        Returns:
            True if state is terminal, False otherwise
            
        Note:
            Terminal states by convention have zero future rewards.
            They may have no possible actions, or equivalently a self-loop
            'pass' action with zero reward.
        """
        return
