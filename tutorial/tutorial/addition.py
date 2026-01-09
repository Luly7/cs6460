"""Addition module for basic arithmetic operations.

This module provides a simple addition function as part of the UC Berkeley
Pacman AI projects tutorial.

Changes from original (2024 Nov 03):
1. Added comprehensive type hints with overloads
2. Used type variables for better type safety
3. Added detailed docstring with examples
4. Better module documentation
5. Used Python 3.13 typing features
6. Added proper return type annotations
7. Better code organization
8. Added doctest examples
9. More maintainable structure

Run python autograder.py to test.

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

from typing import Union, TypeVar, overload

Number = TypeVar('Number', int, float)

@overload
def add(a: int, b: int) -> int: ...

@overload
def add(a: float, b: float) -> float: ...

@overload
def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]: ...

def add(a: Number, b: Number) -> Number:
    """Return the sum of a and b.
    
    Args:
        a: First number to add
        b: Second number to add
        
    Returns:
        The sum of a and b
        
    Examples:
        >>> add(2, 3)
        5
        >>> add(2.0, 3.0)
        5.0
    """
    # ** ADD YOUR CODE HERE **
    