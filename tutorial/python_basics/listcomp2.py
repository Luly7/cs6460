"""Filter and transform strings using list comprehension."""
from typing import List

strings: List[str] = ['Some string', 'Art', 'Music', 'Artificial Intelligence']
filtered_strings: List[str] = [x.lower() for x in strings if len(x) > 5]
print(filtered_strings)