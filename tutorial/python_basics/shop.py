"""A shop class for managing fruit inventory and calculating order costs."""
from typing import Dict, List, Optional, Tuple


class FruitShop:
    """A shop that sells fruit by the pound."""

    def __init__(self, name: str, fruit_prices: Dict[str, float]) -> None:
        """Initialize a new fruit shop.

        Args:
            name: Name of the fruit shop
            fruit_prices: Dictionary mapping fruit names to prices per pound
        """
        self.fruit_prices = fruit_prices
        self.name = name
        print(f'Welcome to {name} fruit shop')

    def get_cost_per_pound(self, fruit: str) -> Optional[float]:
        """Get the price per pound for a specific fruit.

        Args:
            fruit: Name of the fruit

        Returns:
            Cost per pound of the fruit, or None if not in inventory
        """
        if fruit not in self.fruit_prices:
            print(f"Sorry we don't have {fruit}")
            return None
        return self.fruit_prices[fruit]

    def get_price_of_order(self, order_list: List[Tuple[str, float]]) -> float:
        """Calculate the total cost of an order.

        Args:
            order_list: List of (fruit, numPounds) tuples

        Returns:
            Total cost of the order
        """
        total_cost = 0.0
        for fruit, num_pounds in order_list:
            cost_per_pound = self.get_cost_per_pound(fruit)
            if cost_per_pound is not None:
                total_cost += num_pounds * cost_per_pound
        return total_cost

    def get_name(self) -> str:
        """Get the name of the shop."""
        return self.name

    def __str__(self) -> str:
        return f"<FruitShop: {self.get_name()}>"