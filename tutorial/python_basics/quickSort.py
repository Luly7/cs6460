"""Implementation of the QuickSort algorithm."""
from typing import List, TypeVar

T = TypeVar('T', int, float, str)  # Comparable types

def quick_sort(lst: List[T]) -> List[T]:
    """Sort a list using the QuickSort algorithm.
    
    Args:
        lst: List of comparable items to sort
        
    Returns:
        A new sorted list
    """
    if len(lst) <= 1:
        return lst
    
    pivot = lst[0]
    smaller = [x for x in lst[1:] if x < pivot]
    larger = [x for x in lst[1:] if x >= pivot]
    return quick_sort(smaller) + [pivot] + quick_sort(larger)


def main() -> None:
    """Example usage of quick_sort."""
    sample_list = [2, 4, 5, 1]
    print(quick_sort(sample_list))


if __name__ == '__main__':
    main()