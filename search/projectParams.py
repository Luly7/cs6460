"""Project configuration parameters for the Pacman AI project.

This module contains configuration settings used by the autograder and project
infrastructure, including file paths and project metadata.

Original Authors:
    John DeNero (denero@cs.berkeley.edu)
    Dan Klein (klein@cs.berkeley.edu)
    Brad Miller
    Nick Hay
    Pieter Abbeel (pabbeel@cs.berkeley.edu)

Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
"""

from typing import Final

# Default student code files to grade
STUDENT_CODE_DEFAULT: Final[str] = 'searchAgents.py,search.py'

# Test class file containing autograder test cases
PROJECT_TEST_CLASSES: Final[str] = 'searchTestClasses.py'

# Project name/identifier
PROJECT_NAME: Final[str] = 'Project 1: Search'

# Whether to display bonus visualization
BONUS_PIC: Final[bool] = False
