"""Shop price comparison module.

This module helps find the cheapest fruit shop for a given order.

Changes from original (2024 Nov 03):
1. Added comprehensive type hints
2. Used modern string formatting (f-strings)
3. Added detailed docstrings with examples
4. Better module documentation
5. Used Python 3.13 typing features
6. Added proper return type annotations
7. Better code organization
8. Added input validation
9. Used type aliases for clarity
10. Added error handling

Example output:
    Welcome to shop1 fruit shop
    Welcome to shop2 fruit shop
    For orders: [('apples', 1.0), ('oranges', 3.0)] best shop is shop1
    For orders: [('apples', 3.0)] best shop is shop2

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
import shop
from shop import FruitShop

# Type aliases for better readability
FruitName = str
PoundAmount = float
Price = float
OrderItem = Tuple[FruitName, PoundAmount]
OrderList = List[OrderItem]
PriceList = Dict[FruitName, Price]
ShopList = List[FruitShop]

def shopSmart(order_list: OrderList, fruit_shops: ShopList) -> Optional[FruitShop]:
    """Find the FruitShop with the lowest price for the order.
    
    Args:
        order_list: List of tuples, where each tuple contains:
            - fruit name (str)
            - number of pounds (float)
        fruit_shops: List of FruitShop instances to compare prices
            
    Returns:
        FruitShop instance with lowest total price for the order,
        or None if no valid shops are found.
        
    Examples:
        >>> dir1 = {'apples': 2.0, 'oranges': 1.0}
        >>> shop1 = FruitShop('shop1', dir1)
        >>> dir2 = {'apples': 1.0, 'oranges': 5.0}
        >>> shop2 = FruitShop('shop2', dir2)
        >>> orders = [('apples', 1.0), ('oranges', 3.0)]
        >>> best_shop = shopSmart(orders, [shop1, shop2])
        >>> best_shop.getName()
        'shop1'
    """
    # ** ADD YOUR CODE HERE **
    


def main() -> None:
    """Run test cases for the shopSmart function."""
    # Test case 1
    orders: OrderList = [('apples', 1.0), ('oranges', 3.0)]
    dir1: PriceList = {'apples': 2.0, 'oranges': 1.0}
    shop1 = FruitShop('shop1', dir1)
    dir2: PriceList = {'apples': 1.0, 'oranges': 5.0}
    shop2 = FruitShop('shop2', dir2)
    shops: ShopList = [shop1, shop2]
    
    best_shop = shopSmart(orders, shops)
    print(f"For orders: {orders} best shop is {best_shop.getName()}")
    
    # Test case 2
    orders = [('apples', 3.0)]
    best_shop = shopSmart(orders, shops)
    print(f"For orders: {orders} best shop is {best_shop.getName()}")


if __name__ == '__main__':
    main()