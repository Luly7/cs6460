"""Test case file parser for the Pacman AI projects.

This module provides functionality for parsing specially formatted test files used in
autograding. The parser handles test files that specify test cases and expected outputs
using a custom format with properties specified as key-value pairs, supporting both
single-line and multi-line values.

Originally developed at UC Berkeley for CS188 Intro to AI.
Modified by George Rudolph on 12 Nov 2024:
- Added type hints throughout the codebase
- Improved documentation and docstrings
- Verified compatibility with Python 3.13

Original Licensing Information:  
You are free to use or extend these projects for educational purposes provided that
(1) you do not distribute or publish solutions
(2) you retain this notice
(3) you provide clear attribution to UC Berkeley, including a link to http://ai.berkeley.edu

Original Attribution:
The Pacman AI projects were developed at UC Berkeley.
Core projects and autograders created by John DeNero (denero@cs.berkeley.edu) 
and Dan Klein (klein@cs.berkeley.edu).
Student side autograding added by Brad Miller, Nick Hay, and Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""


from typing import Dict, List, Tuple, TextIO
import re
import sys


class TestParser:
    """Parser for test case files used in autograding.
    
    Parses specially formatted test files that specify test cases and expected outputs.
    Test files use a custom format with properties specified as key-value pairs,
    supporting both single-line and multi-line values.
    """

    def __init__(self, path: str) -> None:
        """Initialize parser with path to test file.
        
        Args:
            path: Path to the test file to parse
        """
        self.path = path

    def removeComments(self, rawlines: List[str]) -> str:
        """Remove comments from test file lines.
        
        Removes any portion of lines following a '#' symbol.
        
        Args:
            rawlines: List of raw lines from test file
            
        Returns:
            String with all lines joined and comments removed
        """
        fixed_lines = []
        for l in rawlines:
            idx = l.find('#')
            if idx == -1:
                fixed_lines.append(l)
            else:
                fixed_lines.append(l[0:idx])
        return '\n'.join(fixed_lines)

    def parse(self) -> Dict:
        """Parse the test file into a dictionary of test properties.
        
        Returns:
            Dictionary containing parsed test properties and metadata
        
        Raises:
            SystemExit: If there is an error parsing the test file
        """
        test: Dict = {}
        with open(self.path) as handle:
            raw_lines = handle.read().split('\n')

        test_text = self.removeComments(raw_lines)
        test['__raw_lines__'] = raw_lines
        test['path'] = self.path
        test['__emit__'] = []
        lines = test_text.split('\n')
        i = 0
        
        while(i < len(lines)):
            if re.match('\A\s*\Z', lines[i]):
                test['__emit__'].append(("raw", raw_lines[i]))
                i += 1
                continue
            m = re.match('\A([^"]*?):\s*"([^"]*)"\s*\Z', lines[i])
            if m:
                test[m.group(1)] = m.group(2)
                test['__emit__'].append(("oneline", m.group(1)))
                i += 1
                continue
            m = re.match('\A([^"]*?):\s*"""\s*\Z', lines[i])
            if m:
                msg = []
                i += 1
                while(not re.match('\A\s*"""\s*\Z', lines[i])):
                    msg.append(raw_lines[i])
                    i += 1
                test[m.group(1)] = '\n'.join(msg)
                test['__emit__'].append(("multiline", m.group(1)))
                i += 1
                continue
            print(f'error parsing test file: {self.path}')
            sys.exit(1)
        return test


def emitTestDict(testDict: Dict, handle: TextIO) -> None:
    """Write test dictionary back to file format.
    
    Args:
        testDict: Dictionary containing test data to write
        handle: File handle to write output to
        
    Raises:
        Exception: If the emit type is invalid
    """
    for kind, data in testDict['__emit__']:
        if kind == "raw":
            handle.write(f"{data}\n")
        elif kind == "oneline":
            handle.write(f'{data}: "{testDict[data]}"\n')
        elif kind == "multiline":
            handle.write(f'{data}: """\n{testDict[data]}\n"""\n')
        else:
            raise Exception("Bad __emit__")
