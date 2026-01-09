"""Project parameters for the Pacman AI multiagent search project.

This module defines configuration parameters used by the autograder and testing
framework for Project 2, which focuses on multiagent search algorithms. It specifies
the default student code file, test classes, project name and other settings needed
for running and grading the project.

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

from typing import Final

STUDENT_CODE_DEFAULT: Final[str] = 'multiAgents.py'
PROJECT_TEST_CLASSES: Final[str] = 'multiagentTestClasses.py'
PROJECT_NAME: Final[str] = 'Project 2: Multiagent search'
BONUS_PIC: Final[bool] = False
