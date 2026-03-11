"""Demonstrate list comprehensions with filtering and transformations."""
from typing import List

nums: List[int] = [1, 2, 3, 4, 5, 6]
odd_nums: List[int] = [x for x in nums if x % 2 == 1]
print(odd_nums)
odd_nums_plus_one: List[int] = [x + 1 for x in nums if x % 2 == 1]
print(odd_nums_plus_one)