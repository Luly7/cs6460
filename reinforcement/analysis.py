"""
Analysis Module for Value Iteration and Q-Learning Parameters

This module contains functions that return parameter settings to achieve specific
behaviors in value iteration and Q-learning algorithms. Each question function
returns parameters that produce particular policies in the gridworld environment.

Key Components:
- Value Iteration Parameters: Settings for bridge crossing and navigation
- Q-Learning Parameters: Settings for crawler robot learning
- Test Functions: Validation of parameter effects on agent behavior

Functions:
    question2: Parameters for optimal bridge crossing with value iteration
    question3a-e: Parameters for different gridworld navigation strategies
    question8: Parameters for Q-learning in crawler robot environment
    main: Test function to print all question answers when run standalone

Changes in this version:
- Verified compatibility with Python 3.13
- Improved docstring organization and clarity 
- Added detailed component descriptions
- Updated formatting for better readability

Originally from UC Berkeley CS188 Pacman Projects.
Modified for use in USAFA CS330 course.

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

# Original Pacman AI projects developed at UC Berkeley
# http://ai.berkeley.edu/reinforcement.html
# Attribution: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

######################
# ANALYSIS QUESTIONS #
######################

# Set the given parameters to obtain the specified policies through
# value iteration.


def question2() -> tuple[float, float]:
    answerDiscount = 0.9
    answerNoise = 0.0
    return answerDiscount, answerNoise


def question3a():
    answerDiscount = 0.1
    answerNoise = 0.0
    answerLivingReward = -1.0
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'


def question3b():
    answerDiscount = 0.2
    answerNoise = 0.2
    answerLivingReward = -1.0
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'


def question3c():
    answerDiscount = 0.9
    answerNoise = 0.0
    answerLivingReward = -0.1
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'


def question3d():
    answerDiscount = 0.9
    answerNoise = 0.5
    answerLivingReward = 0.0
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'


def question3e():
    answerDiscount = 0.9
    answerNoise = 0.5
    answerLivingReward = 10.0
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'


def question8():
    answerEpsilon = 0.5
    answerLearningRate = 0.8
    return 'NOT POSSIBLE'
    # If not possible, return 'NOT POSSIBLE'


def main() -> None:
    """
    Test function that prints answers to all analysis questions.
    Only executed when this file is run standalone.
    """
    print('Answers to analysis questions:')
    import analysis
    for q in [q for q in dir(analysis) if q.startswith('question')]:
        response = getattr(analysis, q)()
        print(f'  Question {q}:\t{response}')


if __name__ == '__main__':
    main()
