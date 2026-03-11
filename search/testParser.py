"""Test parser for reading and writing test case files.

This module provides functionality for parsing test case files that contain
key-value pairs and raw text. It handles both single-line and multi-line
property formats and preserves comments and formatting when writing back to files.

Original Licensing Information:
You are free to use or extend these projects for educational purposes provided that
(1) you do not distribute or publish solutions, (2) you retain this notice, and
(3) you provide clear attribution to UC Berkeley, including a link to 
http://ai.berkeley.edu.

Original Attribution:
The Pacman AI projects were developed at UC Berkeley. The core projects and
autograders were primarily created by John DeNero (denero@cs.berkeley.edu) and
Dan Klein (klein@cs.berkeley.edu). Student side autograding was added by
Brad Miller, Nick Hay, and Pieter Abbeel (pabbeel@cs.berkeley.edu).

Author: George Rudolph
Date: 9 Nov 2024
Changes:
- Added type hints throughout
- Improved documentation and docstrings
- f-strings used for string formatting
"""

import re
import sys
from typing import Dict, List, Tuple, TextIO, Any

class TestParser:
    """
    Parser for test case files that contain key-value pairs and raw text.
    
    Handles parsing test files that contain properties in the format:
    key: "value" (single line)
    key: \"\"\" 
    multiline value
    \"\"\" (multiline)
    
    Attributes:
        path (str): Path to the test file to parse
    """

    def __init__(self, path: str) -> None:
        """Initialize parser with path to test file.
        
        Args:
            path: Path to the test file to parse
        """
        self.path = path

    def removeComments(self, rawlines: List[str]) -> str:
        """Remove comments starting with # from lines.
        
        Args:
            rawlines: List of raw input lines
            
        Returns:
            String with all lines joined, comments removed
        """
        fixed_lines = []
        for line in rawlines:
            idx = line.find('#')
            if idx == -1:
                fixed_lines.append(line)
            else:
                fixed_lines.append(line[0:idx])
        return '\n'.join(fixed_lines)

    def parse(self) -> Dict[str, Any]:
        """Parse the test file into a dictionary.
        
        Returns:
            Dictionary containing:
            - Raw lines from file (__raw_lines__)
            - File path (path) 
            - List of emit instructions (__emit__)
            - All parsed key-value pairs from file
            
        Raises:
            SystemExit: If parsing error occurs
        """
        test: Dict[str, Any] = {}
        with open(self.path) as handle:
            raw_lines = handle.read().split('\n')

        test_text = self.removeComments(raw_lines)
        test['__raw_lines__'] = raw_lines
        test['path'] = self.path
        test['__emit__'] = []
        lines = test_text.split('\n')
        i = 0
        
        while i < len(lines):
            # Skip blank lines
            if re.match(r'\A\s*\Z', lines[i]):
                test['__emit__'].append(("raw", raw_lines[i]))
                i += 1
                continue
                
            # Match single line property
            m = re.match(r'\A([^"]*?):\s*"([^"]*)"\s*\Z', lines[i])
            if m:
                test[m.group(1)] = m.group(2)
                test['__emit__'].append(("oneline", m.group(1)))
                i += 1
                continue
                
            # Match multiline property
            m = re.match(r'\A([^"]*?):\s*"""\s*\Z', lines[i])
            if m:
                msg = []
                i += 1
                while not re.match(r'\A\s*"""\s*\Z', lines[i]):
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
    """Write test dictionary back to file handle.
    
    Args:
        testDict: Dictionary containing test data and emit instructions
        handle: File handle to write to
        
    Raises:
        Exception: If invalid emit instruction encountered
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
