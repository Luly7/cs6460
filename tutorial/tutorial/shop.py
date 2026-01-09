"""Fruit shop implementation with modern Python features.

This module provides a FruitShop class for managing fruit prices and orders.
It maintains backward compatibility while using modern Python practices internally.

Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).

Changes:
    2024-03-19: Updated to Python 3.13 standards
    - Added Money value object for currency handling
    - Added type hints throughout
    - Added proper decimal handling for currency
    - Improved error handling and validation
    - Added comparison operators
    - Maintained backward compatibility with original API
    - Updated string formatting to f-strings
    - Added proper documentation
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Tuple, Union, Optional


@dataclass(frozen=True)
class Money:
    """Represents a monetary amount."""
    amount: Decimal

    def __init__(self, amount: Union[str, Decimal, float]) -> None:
        """Initialize with proper decimal conversion."""
        object.__setattr__(self, 'amount', Decimal(str(amount)))

    def __add__(self, other: 'Money') -> 'Money':
        return Money(self.amount + other.amount)

    def __mul__(self, quantity: Union[Decimal, float]) -> 'Money':
        return Money(self.amount * Decimal(str(quantity)))

    def __float__(self) -> float:
        """Support legacy float operations."""
        return float(self.amount)

    def __lt__(self, other: Union['Money', float]) -> bool:
        """Support less than comparisons with Money or float."""
        if isinstance(other, Money):
            return self.amount < other.amount
        return self.amount < Decimal(str(other))

    def __gt__(self, other: Union['Money', float]) -> bool:
        """Support greater than comparisons with Money or float."""
        if isinstance(other, Money):
            return self.amount > other.amount
        return self.amount > Decimal(str(other))

    def __eq__(self, other: Union['Money', float]) -> bool:
        """Support equality comparisons with Money or float."""
        if isinstance(other, Money):
            return self.amount == other.amount
        return self.amount == Decimal(str(other))

    def __str__(self) -> str:
        return f"${self.amount:.2f}"


class FruitShop:
    """A modern fruit shop implementation with legacy support."""

    def __init__(self, name: str, fruitPrices: Dict[str, Union[str, float, Decimal]]) -> None:
        """Initialize shop with name and prices.

        Args:
            name: Name of the fruit shop
            fruitPrices: Dictionary with keys as fruit strings and prices for values
                        e.g. {'apples':2.00, 'oranges': 1.50, 'pears': 1.75}
        """
        self.name = name
        self._prices = {
            fruit.lower(): Money(price)
            for fruit, price in fruitPrices.items()
        }
        print(f"Welcome to {self.name} fruit shop")

    def getCostPerPound(self, fruit: str) -> Optional[float]:
        """Get the cost per pound of a fruit.

        Args:
            fruit: Fruit string

        Returns:
            Cost of 'fruit', assuming 'fruit' is in our inventory or None otherwise
        """
        if price := self._prices.get(fruit.lower()):
            return float(price.amount)
        return None

    def getPriceOfOrder(self, orderList: List[Tuple[str, float]]) -> float:
        """Calculate the total cost of an order.

        Args:
            orderList: List of (fruit, numPounds) tuples

        Returns:
            Cost of orderList, only including the values of fruits that this fruit shop has
        """
        total = self.calculate_order_total(orderList)
        return float(total.amount)

    def calculate_order_total(self, orderList: List[Tuple[str, float]]) -> Money:
        """Modern method: Calculate total cost of order with precise decimal handling.

        Args:
            orderList: List of (fruit, pounds) tuples

        Returns:
            Money object representing total cost
        """
        return sum(
            (self._prices[fruit.lower()] * Decimal(str(pounds))
             for fruit, pounds in orderList
             if fruit.lower() in self._prices),
            start=Money('0')
        )

    def getName(self) -> str:
        """Get the name of the shop.

        Returns:
            Name of the fruit shop
        """
        return self.name

    def __str__(self) -> str:
        """Get string representation of the shop."""
        return f"<FruitShop: {self.getName()}>"

    def __repr__(self) -> str:
        """Get detailed string representation of the shop."""
        return str(self)