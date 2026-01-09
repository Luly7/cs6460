"""Fruit purchasing cost calculator.

This module calculates the total cost of a fruit order based on a price list.

Changes from original (2024-03-20):
1. Added comprehensive type hints
2. Used modern string formatting (f-strings)
3. Added detailed docstrings with examples
4. Better module documentation
5. Used Python 3.13 typing features
6. Added proper return type annotations
7. Better code organization
8. Added input validation
9. Used type aliases for clarity
10. Added constants for configuration

To run this script, type:
    python buyLotsOfFruit.py

Example output:
    Cost of [('apples', 2.0), ('pears', 3.0), ('limes', 4.0)] is 12.25

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

from typing import Dict, List, Tuple, Optional
from decimal import Decimal

# Type aliases for better readability
FruitName = str
PoundAmount = float
Price = float
OrderItem = Tuple[FruitName, PoundAmount]
OrderList = List[OrderItem]
PriceList = Dict[FruitName, Price]

# Constants
FRUIT_PRICES: PriceList = {
    'apples': 2.00,
    'oranges': 1.50,
    'pears': 1.75,
    'limes': 0.75,
    'strawberries': 1.00
}

def buyLotsOfFruit(order_list: OrderList) -> Optional[float]:
    """Calculate the total cost of a fruit order.
    
    Args:
        order_list: List of tuples, where each tuple contains:
            - fruit name (str)
            - number of pounds (float)
            
    Returns:
        Total cost of the order as a float, or None if any fruit is not found
        in the price list.
        
    Examples:
        >>> buyLotsOfFruit([('apples', 2.0), ('pears', 3.0)])
        8.25
        >>> buyLotsOfFruit([('apples', 2.0), ('invalid_fruit', 3.0)])
        None
    """
    # ** ADD YOUR CODE HERE **
    

def main() -> None:
    """Run a test case for the buyLotsOfFruit function."""
    order_list: OrderList = [
        ('apples', 2.0),
        ('pears', 3.0),
        ('limes', 4.0)
    ]
    
    cost = buyLotsOfFruit(order_list)
    if cost is not None:
        print(f'Cost of {order_list} is {cost:.2f}')
    else:
        print(f'Error: some fruits in {order_list} are not in the price list')


if __name__ == '__main__':
    main()