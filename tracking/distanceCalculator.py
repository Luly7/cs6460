"""
distanceCalculator.py
--------------------
This module provides distance calculation functionality for the Pacman AI projects.
It implements efficient maze distance computation and caching between any two points
in the game layout.

Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).

Modified 19 Dec 2024 by George Rudolph:
- Verified compatibility with Python 3.13
- Added comprehensive module docstring
- Improved code organization and documentation
- Enhanced type hints and error handling
"""


"""
This file contains a Distancer object which computes and
caches the shortest path between any two points in the maze. It
returns a Manhattan distance between two points if the maze distance
has not yet been calculated.

Example:
    distancer = Distancer(gameState.data.layout)
    distancer.getDistance((1,1), (10,10))

The Distancer object also serves as an example of sharing data
safely among agents via a global dictionary (distanceMap),
and performing asynchronous computation via threads. These
examples may help you in designing your own objects, but you
shouldn't need to modify the Distancer code in order to use its
distances.
"""

import threading, sys, time, random
from typing import Dict, List, Tuple, Optional, Union, Any


class Distancer:
    def __init__(self, layout: Any, background: bool = True, default: int = 10000) -> None:
        """
        Initialize with Distancer(layout). Changing default is unnecessary.

        Args:
            layout: The game layout
            background: If True, compute distances in background thread
            default: Default distance value
            
        This will start computing maze distances in the background and use them
        as soon as they are ready. In the meantime, it returns manhattan distance.

        To compute all maze distances on initialization, set background=False
        """
        self._distances: Optional[Dict] = None
        self.default = default

        # Start computing distances in the background; when the dc finishes,
        # it will fill in self._distances for us.
        dc = DistanceCalculator()
        dc.setAttr(layout, self)
        dc.setDaemon(True)
        if background:
            dc.start()
        else:
            dc.run()

    def getDistance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """
        The getDistance function is the only one you'll need after you create the object.
        
        Args:
            pos1: First position tuple (x,y)
            pos2: Second position tuple (x,y)
            
        Returns:
            float: Distance between the two positions
        """
        if self._distances == None:
            return manhattanDistance(pos1, pos2)
        if isInt(pos1) and isInt(pos2):
            return self.getDistanceOnGrid(pos1, pos2)
        pos1Grids = getGrids2D(pos1)
        pos2Grids = getGrids2D(pos2)
        bestDistance = self.default
        for pos1Snap, snap1Distance in pos1Grids:
            for pos2Snap, snap2Distance in pos2Grids:
                gridDistance = self.getDistanceOnGrid(pos1Snap, pos2Snap)
                distance = gridDistance + snap1Distance + snap2Distance
                if bestDistance > distance:
                    bestDistance = distance
        return bestDistance

    def getDistanceOnGrid(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Get the distance between two grid positions.
        
        Args:
            pos1: First grid position tuple (x,y)
            pos2: Second grid position tuple (x,y)
            
        Returns:
            float: Grid distance between positions
            
        Raises:
            Exception: If positions not in grid
        """
        key = (pos1, pos2)
        if key in self._distances:
            return self._distances[key]
        else:
            raise Exception(f"Positions not in grid: {key}")

    def isReadyForMazeDistance(self) -> bool:
        """
        Check if maze distances have been computed.
        
        Returns:
            bool: True if distances are ready
        """
        return self._distances != None


def manhattanDistance(x: Tuple[float, float], y: Tuple[float, float]) -> float:
    """Calculate Manhattan distance between two points."""
    return abs(x[0] - y[0]) + abs(x[1] - y[1])


def isInt(pos: Tuple[float, float]) -> bool:
    """Check if a position tuple contains integer coordinates."""
    x, y = pos
    return x == int(x) and y == int(y)


def getGrids2D(pos: Tuple[float, float]) -> List[Tuple[Tuple[int, int], float]]:
    """Get 2D grid positions and distances for a position."""
    grids = []
    for x, xDistance in getGrids1D(pos[0]):
        for y, yDistance in getGrids1D(pos[1]):
            grids.append(((x, y), xDistance + yDistance))
    return grids


def getGrids1D(x: float) -> List[Tuple[int, float]]:
    """Get 1D grid positions and distances for a coordinate."""
    intX = int(x)
    if x == int(x):
        return [(x, 0)]
    return [(intX, x - intX), (intX + 1, intX + 1 - x)]


##########################################
# MACHINERY FOR COMPUTING MAZE DISTANCES #
##########################################

distanceMap: Dict = {}
distanceMapSemaphore = threading.Semaphore(1)
distanceThread: Optional[threading.Thread] = None


def waitOnDistanceCalculator(t: float) -> None:
    """Wait for distance calculator thread."""
    global distanceThread
    if distanceThread != None:
        time.sleep(t)


class DistanceCalculator(threading.Thread):
    def setAttr(self, layout: Any, distancer: Distancer, default: int = 10000) -> None:
        """Set calculator attributes."""
        self.layout = layout
        self.distancer = distancer
        self.default = default

    def run(self) -> None:
        """Run the distance calculation."""
        global distanceMap, distanceThread
        distanceMapSemaphore.acquire()

        if self.layout.walls not in distanceMap:
            if distanceThread != None:
                raise Exception("Multiple distance threads")
            distanceThread = self

            distances = computeDistances(self.layout)
            print("[Distancer]: Switching to maze distances", file=sys.stdout)

            distanceMap[self.layout.walls] = distances
            distanceThread = None
        else:
            distances = distanceMap[self.layout.walls]

        distanceMapSemaphore.release()
        self.distancer._distances = distances


def computeDistances(layout: Any) -> Dict[Tuple[Tuple[int, int], Tuple[int, int]], float]:
    """Compute all pairwise distances in the maze."""
    distances = {}
    allNodes = layout.walls.asList(False)
    for source in allNodes:
        dist = {}
        closed = {}
        for node in allNodes:
            dist[node] = 1000000000
        import util

        queue = util.PriorityQueue()
        queue.push(source, 0)
        dist[source] = 0
        while not queue.isEmpty():
            node = queue.pop()
            if node in closed:
                continue
            closed[node] = True
            nodeDist = dist[node]
            adjacent = []
            x, y = node
            if not layout.isWall((x, y + 1)):
                adjacent.append((x, y + 1))
            if not layout.isWall((x, y - 1)):
                adjacent.append((x, y - 1))
            if not layout.isWall((x + 1, y)):
                adjacent.append((x + 1, y))
            if not layout.isWall((x - 1, y)):
                adjacent.append((x - 1, y))
            for other in adjacent:
                if not other in dist:
                    continue
                oldDist = dist[other]
                newDist = nodeDist + 1
                if newDist < oldDist:
                    dist[other] = newDist
                    queue.push(other, newDist)
        for target in allNodes:
            distances[(target, source)] = dist[target]
    return distances


def getDistanceOnGrid(distances: Dict, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """Get the distance between two grid positions from a distance map."""
    key = (pos1, pos2)
    if key in distances:
        return distances[key]
    return 100000
