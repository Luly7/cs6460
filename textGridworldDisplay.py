

"""
Text-based display for Gridworld Markov Decision Process environments.

This module provides classes and functions for displaying Gridworld MDPs and their
solutions in a text-based format. It visualizes key MDP components including:

- State values (V(s)) displayed as numbers in grid cells
- Optimal policies (π(s)) shown as directional arrows 
- Q-values (Q(s,a)) displayed in quarters of each cell
- Current agent state highlighted with special markers
- Grid layout with walls and terminal states

The display uses ASCII characters and table formatting to create a clear
visualization of the MDP state space and solution components.

Key Features:
- Configurable display of values, policies and Q-values
- Support for highlighting current state and start state
- Automatic table formatting and alignment
- Clear visualization of walls and terminal states

Python Version: 3.13
Last Modified: 23 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Verified Python 3.13 compatibility 
- Improved code documentation
- Added type hints

# textGridworldDisplay.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

import util
from functools import reduce
from typing import Dict, List, Optional, Tuple, Any, Union

class TextGridworldDisplay:
    """
    A class for displaying Gridworld MDPs and agent information in text format.
    
    Displays state values, policies, and Q-values in a grid layout using ASCII characters.
    Can highlight the current state and show directional policies.
    """

    def __init__(self, gridworld: 'gridworld.Gridworld') -> None:
        """
        Initialize the display with a Gridworld environment.
        
        Args:
            gridworld: The Gridworld environment to display
        """
        self.gridworld = gridworld

    def start(self) -> None:
        """Initialize the display. Currently a no-op."""
        pass

    def pause(self) -> None:
        """Pause the display. Currently a no-op."""
        pass

    def displayValues(self, agent: Any, currentState: Optional[Tuple[int, int]] = None, message: Optional[str] = None) -> None:
        """
        Display the agent's value function and policy.
        
        Args:
            agent: The agent whose values/policy to display
            currentState: The current state to highlight (optional)
            message: A message to display above the grid (optional)
        """
        if message is not None:
            print(message)
        values = util.Counter()
        policy = {}
        states = self.gridworld.getStates()
        for state in states:
            values[state] = agent.getValue(state)
            policy[state] = agent.getPolicy(state)
        prettyPrintValues(self.gridworld, values, policy, currentState)

    def displayNullValues(self, agent: Any, currentState: Optional[Tuple[int, int]] = None, message: Optional[str] = None) -> None:
        """
        Display the gridworld with no values, just the grid layout.
        
        Args:
            agent: The agent (unused)
            currentState: The current state to highlight (optional)
            message: A message to display above the grid (optional)
        """
        if message is not None: print(message)
        prettyPrintNullValues(self.gridworld, currentState)

    def displayQValues(self, agent: Any, currentState: Optional[Tuple[int, int]] = None, message: Optional[str] = None) -> None:
        """
        Display the agent's Q-values.
        
        Args:
            agent: The agent whose Q-values to display
            currentState: The current state to highlight (optional)
            message: A message to display above the grid (optional)
        """
        if message is not None: print(message)
        qValues = util.Counter()
        states = self.gridworld.getStates()
        for state in states:
            for action in self.gridworld.getPossibleActions(state):
                qValues[(state, action)] = agent.getQValue(state, action)
        prettyPrintQValues(self.gridworld, qValues, currentState)


def prettyPrintValues(gridWorld: 'gridworld.Gridworld', values: Dict, policy: Optional[Dict] = None, currentState: Optional[Tuple[int, int]] = None) -> None:
    """
    Print a visualization of the values and policy in a grid layout.
    
    Args:
        gridWorld: The Gridworld environment
        values: Dictionary mapping states to values
        policy: Dictionary mapping states to actions (optional)
        currentState: The current state to highlight (optional)
    """
    grid = gridWorld.grid
    maxLen = 11
    newRows = []
    for y in range(grid.height):
        newRow = []
        for x in range(grid.width):
            state = (x, y)
            value = values[state]
            action = None
            if policy != None and state in policy:
                action = policy[state]
            actions = gridWorld.getPossibleActions(state)
            if action not in actions and 'exit' in actions:
                action = 'exit'
            valString = None
            if action == 'exit':
                valString = border(f'{value:.2f}')
            else:
                valString = f'\n\n{value:.2f}\n\n'
                valString += ' '*maxLen
            if grid[x][y] == 'S':
                valString = f'\n\nS: {value:.2f}\n\n'
                valString += ' '*maxLen
            if grid[x][y] == '#':
                valString = '\n#####\n#####\n#####\n'
                valString += ' '*maxLen
            pieces = [valString]
            text = ("\n".join(pieces)).split('\n')
            if currentState == state:
                l = len(text[1])
                if l == 0:
                    text[1] = '*'
                else:
                    text[1] = "|" + ' ' * int((l-1)/2-1) + '*' + ' ' * int((l)/2-1) + "|"
            if action == 'east':
                text[2] = '  ' + text[2]  + ' >'
            elif action == 'west':
                text[2] = '< ' + text[2]  + '  '
            elif action == 'north':
                text[0] = ' ' * int(maxLen/2) + '^' +' ' * int(maxLen/2)
            elif action == 'south':
                text[4] = ' ' * int(maxLen/2) + 'v' +' ' * int(maxLen/2)
            newCell = "\n".join(text)
            newRow.append(newCell)
        newRows.append(newRow)
    numCols = grid.width
    for rowNum, row in enumerate(newRows):
        row.insert(0,f"\n\n{rowNum}")
    newRows.reverse()
    colLabels = [str(colNum) for colNum in range(numCols)]
    colLabels.insert(0,' ')
    finalRows = [colLabels] + newRows
    print(indent(finalRows,separateRows=True,delim='|', prefix='|',postfix='|', justify='center',hasHeader=True))


def prettyPrintNullValues(gridWorld: 'gridworld.Gridworld', currentState: Optional[Tuple[int, int]] = None) -> None:
    """
    Print a visualization of just the grid layout with no values.
    
    Args:
        gridWorld: The Gridworld environment
        currentState: The current state to highlight (optional)
    """
    grid = gridWorld.grid
    maxLen = 11
    newRows = []
    for y in range(grid.height):
        newRow = []
        for x in range(grid.width):
            state = (x, y)

            # value = values[state]

            action = None
            # if policy != None and state in policy:
            #   action = policy[state]
            #
            actions = gridWorld.getPossibleActions(state)

            if action not in actions and 'exit' in actions:
                action = 'exit'

            valString = None
            # if action == 'exit':
            #   valString = border('%.2f' % value)
            # else:
            #   valString = '\n\n%.2f\n\n' % value
            #   valString += ' '*maxLen

            if grid[x][y] == 'S':
                valString = '\n\nS\n\n'
                valString += ' '*maxLen
            elif grid[x][y] == '#':
                valString = '\n#####\n#####\n#####\n'
                valString += ' '*maxLen
            elif type(grid[x][y]) == float or type(grid[x][y]) == int:
                valString = border(f'{float(grid[x][y]):.2f}')
            else: valString = border('  ')
            pieces = [valString]

            text = ("\n".join(pieces)).split('\n')

            if currentState == state:
                l = len(text[1])
                if l == 0:
                    text[1] = '*'
                else:
                    text[1] = "|" + ' ' * int((l-1)/2-1) + '*' + ' ' * int((l)/2-1) + "|"

            if action == 'east':
                text[2] = '  ' + text[2]  + ' >'
            elif action == 'west':
                text[2] = '< ' + text[2]  + '  '
            elif action == 'north':
                text[0] = ' ' * int(maxLen/2) + '^' +' ' * int(maxLen/2)
            elif action == 'south':
                text[4] = ' ' * int(maxLen/2) + 'v' +' ' * int(maxLen/2)
            newCell = "\n".join(text)
            newRow.append(newCell)
        newRows.append(newRow)
    numCols = grid.width
    for rowNum, row in enumerate(newRows):
        row.insert(0,f"\n\n{rowNum}")
    newRows.reverse()
    colLabels = [str(colNum) for colNum in range(numCols)]
    colLabels.insert(0,' ')
    finalRows = [colLabels] + newRows
    print(indent(finalRows,separateRows=True,delim='|', prefix='|',postfix='|', justify='center',hasHeader=True))

def prettyPrintQValues(gridWorld: 'gridworld.Gridworld', qValues: Dict, currentState: Optional[Tuple[int, int]] = None) -> None:
    """
    Print a visualization of Q-values in a grid layout.
    
    Args:
        gridWorld: The Gridworld environment
        qValues: Dictionary mapping (state,action) pairs to Q-values
        currentState: The current state to highlight (optional)
    """
    grid = gridWorld.grid
    maxLen = 11
    newRows = []
    for y in range(grid.height):
        newRow = []
        for x in range(grid.width):
            state = (x, y)
            actions = gridWorld.getPossibleActions(state)
            if actions == None or len(actions) == 0:
                actions = [None]
            bestQ = max([qValues[(state, action)] for action in actions])
            bestActions = [action for action in actions if qValues[(state, action)] == bestQ]

            # display cell
            qStrings = dict([(action, f"{qValues[(state, action)]:.2f}") for action in actions])
            northString = ('north' in qStrings and qStrings['north']) or ' '
            southString = ('south' in qStrings and qStrings['south']) or ' '
            eastString = ('east' in qStrings and qStrings['east']) or ' '
            westString = ('west' in qStrings and qStrings['west']) or ' '
            exitString = ('exit' in qStrings and qStrings['exit']) or ' '

            eastLen = len(eastString)
            westLen = len(westString)
            if eastLen < westLen:
                eastString = ' '*(westLen-eastLen)+eastString
            if westLen < eastLen:
                westString = westString+' '*(eastLen-westLen)

            if 'north' in bestActions:
                northString = '/'+northString+'\\'
            if 'south' in bestActions:
                southString = '\\'+southString+'/'
            if 'east' in bestActions:
                eastString = ''+eastString+'>'
            else:
                eastString = ''+eastString+' '
            if 'west' in bestActions:
                westString = '<'+westString+''
            else:
                westString = ' '+westString+''
            if 'exit' in bestActions:
                exitString = '[ '+exitString+' ]'


            ewString = westString + "     " + eastString
            if state == currentState:
                ewString = westString + "  *  " + eastString
            if state == gridWorld.getStartState():
                ewString = westString + "  S  " + eastString
            if state == currentState and state == gridWorld.getStartState():
                ewString = westString + " S:* " + eastString

            text = [northString, "\n"+exitString, ewString, ' '*maxLen+"\n", southString]

            if grid[x][y] == '#':
                text = ['', '\n#####\n#####\n#####', '']

            newCell = "\n".join(text)
            newRow.append(newCell)
        newRows.append(newRow)
    numCols = grid.width
    for rowNum, row in enumerate(newRows):
        row.insert(0,f"\n\n\n{rowNum}")
    newRows.reverse()
    colLabels = [str(colNum) for colNum in range(numCols)]
    colLabels.insert(0,' ')
    finalRows = [colLabels] + newRows

    print(indent(finalRows,separateRows=True,delim='|',prefix='|',postfix='|', justify='center',hasHeader=True))

def border(text: str) -> str:
    """
    Add a border around text using ASCII characters.
    
    Args:
        text: The text to border
        
    Returns:
        The text with an ASCII border around it
    """
    length = len(text)
    pieces = ['-' * (length+2), '|'+' ' * (length+2)+'|', f' | {text} | ', '|'+' ' * (length+2)+'|','-' * (length+2)]
    return '\n'.join(pieces)

# INDENTING CODE

# Indenting code based on a post from George Sakkis
# (http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/267662)

import io,operator

def indent(rows: List[List[str]], hasHeader: bool = False, headerChar: str = '-', delim: str = ' | ', justify: str = 'left',
           separateRows: bool = False, prefix: str = '', postfix: str = '', wrapfunc: Any = lambda x:x) -> str:
    """
    Indents a table by column.
    
    Args:
        rows: A sequence of sequences of items, one sequence per row
        hasHeader: True if the first row consists of column names
        headerChar: Character for row separator line
        delim: The column delimiter
        justify: How to justify data ('left','right','center')
        separateRows: True to separate rows with headerChar line
        prefix: String prepended to each printed row
        postfix: String appended to each printed row
        wrapfunc: Function f(text) for wrapping text
        
    Returns:
        The formatted table as a string
    """
    # closure for breaking logical rows to physical, using wrapfunc
    def rowWrapper(row):
        newRows = [wrapfunc(item).split('\n') for item in row]
        return [[substr or '' for substr in item] for item in list(*newRows)]
    # break each logical row into one or more physical ones
    logicalRows = [rowWrapper(row) for row in rows]
    # columns of physical rows
    columns = list(*reduce(operator.add,logicalRows))
    # get the maximum of each column by the string length of its items
    maxWidths = [max([len(str(item)) for item in column]) for column in columns]
    rowSeparator = headerChar * (len(prefix) + len(postfix) + sum(maxWidths) + \
                                 len(delim)*(len(maxWidths)-1))
    # select the appropriate justify method
    justify = {'center':str.center, 'right':str.rjust, 'left':str.ljust}[justify.lower()]
    output=io.StringIO()
    if separateRows: print(rowSeparator, file=output)
    for physicalRows in logicalRows:
        for row in physicalRows:
            print(prefix \
                + delim.join([justify(str(item),width) for (item,width) in zip(row,maxWidths)]) \
                + postfix, file=output)
        if separateRows or hasHeader: print(rowSeparator, file=output); hasHeader=False
    return output.getvalue()

import math
def wrap_always(text: str, width: int) -> str:
    """
    A simple word-wrap function that wraps text on exactly width characters.
    Does not split text on word boundaries.
    
    Args:
        text: The text to wrap
        width: The width to wrap at
        
    Returns:
        The wrapped text
    """
    return '\n'.join([ text[width*i:width*(i+1)] \
                       for i in range(int(math.ceil(1.*len(text)/width))) ])


# TEST OF DISPLAY CODE

if __name__ == '__main__':
    import gridworld, util

    grid = gridworld.getCliffGrid3()
    print(grid.getStates())

    policy = dict([(state,'east') for state in grid.getStates()])
    values = util.Counter(dict([(state,1000.23) for state in grid.getStates()]))
    prettyPrintValues(grid, values, policy, currentState = (0,0))

    stateCrossActions = [[(state, action) for action in grid.getPossibleActions(state)] for state in grid.getStates()]
    qStates = reduce(lambda x,y: x+y, stateCrossActions, [])
    qValues = util.Counter(dict([((state, action), 10.5) for state, action in qStates]))
    qValues = util.Counter(dict([((state, action), 10.5) for state, action in reduce(lambda x,y: x+y, stateCrossActions, [])]))
    prettyPrintQValues(grid, qValues, currentState = (0,0))
