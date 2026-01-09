"""Demonstrate iteration over lists and dictionaries with price checking."""
from typing import Dict, List

# ... existing code ...
fruits: List[str] = ['apples', 'oranges', 'pears', 'bananas']
for fruit in fruits:
    print(f'{fruit} for sale')

fruit_prices: Dict[str, float] = {'apples': 2.00, 'oranges': 1.50, 'pears': 1.75}
for fruit, price in fruit_prices.items():
    if price < 2.00:
        print(f'{fruit} cost {price:.2f} a pound')
    else:
        print(f'{fruit} are too expensive!')