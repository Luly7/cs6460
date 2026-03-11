"""
Test case parser for autograding framework.

This module provides functionality to parse test case files and emit test dictionaries.
Test files use a custom format with properties specified as key-value pairs. The parser
handles comments, key-value extraction, and validation of the test file format.

Classes:
    TestParser: Parses test case files into dictionaries, handling comments and validation

Functions:
    emitTestDict: Writes a test dictionary back to file format, preserving structure

Usage:
    parser = TestParser(test_file_path)
    test_dict = parser.parse()
    emitTestDict(test_dict, output_file)

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added usage examples
- Added function details
- Improved class descriptions
- Verified Python 3.13 compatibility
- Added modifier attribution

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


import re
import sys
from typing import Dict, List, Tuple, TextIO, Any


class TestParser:
    """Parser for test case files."""

    def __init__(self, path: str) -> None:
        """Initialize parser with test file path.
        
        Args:
            path: Path to test case file
        """
        # save the path to the test file
        self.path = path

    def removeComments(self, rawlines: List[str]) -> str:
        """Remove comments from test file lines.
        
        Args:
            rawlines: List of raw lines from test file
            
        Returns:
            String with all comments removed
        """
        # remove any portion of a line following a '#' symbol
        fixed_lines = []
        for l in rawlines:
            idx = l.find('#')
            if idx == -1:
                fixed_lines.append(l)
            else:
                fixed_lines.append(l[0:idx])
        return '\n'.join(fixed_lines)

    def parse(self) -> Dict[str, Any]:
        """Parse test file into dictionary.
        
        Returns:
            Dictionary containing parsed test case data
        
        Raises:
            SystemExit: If parsing error occurs
        """
        # read in the test case and remove comments
        test = {}
        with open(self.path) as handle:
            raw_lines = handle.read().split('\n')

        test_text = self.removeComments(raw_lines)
        test['__raw_lines__'] = raw_lines
        test['path'] = self.path
        test['__emit__'] = []
        lines = test_text.split('\n')
        i = 0
        # read a property in each loop cycle
        while(i < len(lines)):
            # skip blank lines
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

def emitTestDict(testDict: Dict[str, Any], handle: TextIO) -> None:
    """Write test dictionary back to file format.
    
    Args:
        testDict: Dictionary containing test data
        handle: File handle to write to
        
    Raises:
        Exception: If invalid emit type encountered
    """
    for kind, data in testDict['__emit__']:
        if kind == "raw":
            handle.write(f'{data}\n')
        elif kind == "oneline":
            handle.write(f'{data}: "{testDict[data]}"\n')
        elif kind == "multiline":
            handle.write(f'{data}: """\n{testDict[data]}\n"""\n')
        else:
            raise Exception("Bad __emit__")
