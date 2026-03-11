"""Utility functions and data structures for the Pacman AI projects.

This module provides various utility functions and data structures used throughout
the Pacman AI projects, including specialized containers and mathematical helpers.

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

from __future__ import annotations
from collections import defaultdict, deque, Counter as CollectionsCounter
from dataclasses import dataclass, field
from typing import (
    Any, Dict, List, Optional, Tuple, Union, TypeVar, 
    Generic, Callable, Iterator, DefaultDict, Deque
)
import heapq
import inspect
import random
import signal
import sys
import time
from functools import total_ordering

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class Stack(Generic[T]):
    """A container with a last-in-first-out (LIFO) queuing policy.
    
    This implementation uses collections.deque for better performance.
    """

    def __init__(self) -> None:
        self.list: Deque[T] = deque()
        # Keep track of operations for testing/debugging
        self._push_count: int = 0
        self._pop_count: int = 0

    def push(self, item: T) -> None:
        """Push 'item' onto the stack."""
        self.list.append(item)
        self._push_count += 1

    def pop(self) -> T:
        """Pop the most recently pushed item from the stack."""
        self._pop_count += 1
        return self.list.pop()

    def isEmpty(self) -> bool:
        """Return True if the stack is empty."""
        return len(self.list) == 0
        
    def __len__(self) -> int:
        """Return the number of items in the stack."""
        return len(self.list)
        
    def __str__(self) -> str:
        """Return a string representation of the stack."""
        return str(list(self.list))


class Queue(Generic[T]):
    """A container with a first-in-first-out (FIFO) queuing policy.
    
    This implementation uses collections.deque for better performance.
    """

    def __init__(self) -> None:
        self.list: Deque[T] = deque()
        # Keep track of operations for testing/debugging
        self._push_count: int = 0
        self._pop_count: int = 0

    def push(self, item: T) -> None:
        """Enqueue the 'item' into the queue."""
        self.list.append(item)
        self._push_count += 1

    def pop(self) -> T:
        """
        Dequeue the earliest enqueued item still in the queue.
        This operation removes the item from the queue.
        """
        self._pop_count += 1
        return self.list.popleft()

    def isEmpty(self) -> bool:
        """Return True if the queue is empty."""
        return len(self.list) == 0
        
    def __len__(self) -> int:
        """Return the number of items in the queue."""
        return len(self.list)
        
    def __str__(self) -> str:
        """Return a string representation of the queue."""
        return str(list(self.list))


@total_ordering
class PriorityQueueItem(Generic[T]):
    """A wrapper for items in a priority queue with comparison based on priority."""
    
    def __init__(self, item: T, priority: float, count: int):
        self.item = item
        self.priority = priority
        self.count = count  # Used as a tiebreaker for stable sorting
        
    def __lt__(self, other: 'PriorityQueueItem') -> bool:
        return (self.priority, self.count) < (other.priority, other.count)
        
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PriorityQueueItem):
            return NotImplemented
        return (self.priority, self.count) == (other.priority, other.count)


class PriorityQueue(Generic[T]):
    """
    A container with a priority queue policy.
    
    This implementation uses heapq for better performance and adds
    a count parameter to ensure FIFO behavior for items with the same priority.
    """

    def __init__(self) -> None:
        """Initialize an empty priority queue."""
        self.heap: List[PriorityQueueItem[T]] = []
        self.count: int = 0
        # Keep track of operations for testing/debugging
        self._push_count: int = 0
        self._pop_count: int = 0

    def push(self, item: T, priority: float) -> None:
        """Push 'item' onto the priority queue with priority 'priority'."""
        entry = PriorityQueueItem(item, priority, self.count)
        heapq.heappush(self.heap, entry)
        self.count += 1
        self._push_count += 1

    def pop(self) -> T:
        """Pop and return the item with the lowest priority."""
        if self.isEmpty():
            raise IndexError("pop from an empty priority queue")
        self._pop_count += 1
        return heapq.heappop(self.heap).item

    def isEmpty(self) -> bool:
        """Return True if the priority queue is empty."""
        return len(self.heap) == 0
        
    def __len__(self) -> int:
        """Return the number of items in the priority queue."""
        return len(self.heap)
        
    def __str__(self) -> str:
        """Return a string representation of the priority queue."""
        return str([(entry.item, entry.priority) for entry in self.heap])


class PriorityQueueWithFunction(PriorityQueue[T]):
    """
    A priority queue where the priority is determined by a function.
    
    This implementation maintains compatibility with the original while
    using the modernized PriorityQueue as its base.
    """

    def __init__(self, priorityFunction: Callable[[T], float]):
        """
        Initialize a priority queue with a priority function.
        
        priorityFunction (item) -> priority
        """
        super().__init__()
        self.priorityFunction = priorityFunction

    def push(self, item: T, priority: Optional[float] = None) -> None:
        """
        Push 'item' onto the priority queue with priority from the function.
        
        If priority is provided, it will be used instead of calling the function.
        """
        if priority is None:
            priority = self.priorityFunction(item)
        super().push(item, priority)


class Counter(CollectionsCounter[K]):
    """
    A counter keeps track of counts for a set of keys.
    
    This implementation extends collections.Counter with additional methods
    needed for compatibility with the original Counter class.
    """
    
    def __init__(self, items: Union[Dict[K, Union[int, float]], List[K], None] = None) -> None:
        """Initialize a new counter from an existing counter, dict, list, or None."""
        super().__init__()
        if items is not None:
            self.update(items)

    def incrementAll(self, keys: List[K], count: Union[int, float]) -> None:
        """Increments all elements of keys by the same count."""
        for key in keys:
            self[key] = self.get(key, 0) + count

    def argMax(self) -> Optional[K]:
        """Returns the key with the highest value."""
        if not self:
            return None
        return max(self.items(), key=lambda x: x[1])[0]

    def sortedKeys(self) -> List[K]:
        """Returns a list of keys sorted by their values."""
        return [k for k, _ in sorted(self.items(), key=lambda x: (-x[1], x[0]))]

    def totalCount(self) -> Union[int, float]:
        """Returns the sum of counts for all keys."""
        return sum(self.values())

    def normalize(self) -> None:
        """Normalizes all values to sum to 1."""
        total = float(self.totalCount())
        if total == 0:
            return
        for key in self:
            self[key] = self[key] / total

    def divideAll(self, divisor: Union[int, float]) -> None:
        """Divides all counts by divisor."""
        for key in self:
            self[key] /= divisor

    def copy(self) -> 'Counter[K]':
        """Returns a copy of the counter."""
        return Counter(dict(self))

    def __mul__(self, y: Union[int, float]) -> 'Counter[K]':
        """Multiplies all counts by y."""
        result = Counter()
        for key, value in self.items():
            result[key] = value * y
        return result

    def __radd__(self, y: Union[int, float]) -> 'Counter[K]':
        """Adds y to all counts."""
        result = Counter()
        for key, value in self.items():
            result[key] = value + y
        return result


class TimeoutFunctionException(Exception):
    """Exception to raise on a timeout."""
    pass


class TimeoutFunction:
    """Function wrapper that raises a TimeoutFunctionException after timeout."""

    def __init__(self, function: Callable, timeout: int):
        self.timeout = timeout
        self.function = function

    def handle_timeout(self, signum: int, frame: Any) -> None:
        """Signal handler for timeout."""
        raise TimeoutFunctionException()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the wrapped function with timeout handling."""
        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.timeout)
            try:
                result = self.function(*args, **kwargs)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            return result
        else:
            # No signal.SIGALRM on Windows
            # This won't work reliably on Windows, but it's better than nothing
            import threading
            timeout_happened = [False]
            
            def timeout_function():
                timeout_happened[0] = True
                
            timer = threading.Timer(self.timeout, timeout_function)
            timer.start()
            try:
                result = self.function(*args, **kwargs)
            finally:
                timer.cancel()
            if timeout_happened[0]:
                raise TimeoutFunctionException()
            return result


# Global print muting functionality
_ORIGINAL_STDOUT: Optional[Any] = None
_MUTED: bool = False


class WritableNull:
    """File-like object that discards everything written to it."""
    
    def write(self, string: str) -> None:
        """Discard the string."""
        pass


def mutePrint() -> None:
    """Mute print statements by redirecting stdout to a null writer."""
    global _ORIGINAL_STDOUT
    _ORIGINAL_STDOUT = sys.stdout
    sys.stdout = WritableNull()


def unmutePrint() -> None:
    """Unmute print statements by restoring original stdout."""
    global _ORIGINAL_STDOUT
    if _ORIGINAL_STDOUT is not None:
        sys.stdout = _ORIGINAL_STDOUT
        _ORIGINAL_STDOUT = None


_ORIGINAL_STDOUT = None


class FixedRandom:
    """Random number generator with a fixed seed for reproducibility."""
    
    def __init__(self):
        self.reset()

    def reset(self) -> None:
        """Reset the random number generator with a fixed seed."""
        self.random = random.Random(42).random
        
    def random(self) -> float:
        """Return a random float in [0, 1)."""
        # This will be overwritten in reset()
        return 0.0