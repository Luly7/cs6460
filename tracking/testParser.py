"""Test file parser for Pacman AI project autograding.

This module provides functionality for parsing test case files used in autograding,
including:
- Parsing test files into dictionaries of test data and metadata
- Handling single and multi-line test properties 
- Comment removal and preprocessing
- Test case validation and error checking

Changes by George Rudolph 30 Nov 2024:
- Added comprehensive module docstring
- Added type hints throughout
- Improved class and method documentation
- Enhanced error handling and validation
- Standardized code formatting

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


import re
import sys
from typing import List, Dict, Any, Tuple


class TestParser(object):
    def __init__(self, path: str) -> None:
        """Initialize test parser with path to test file.
        
        Args:
            path: Path to the test file to parse
        """
        self.path = path

    def removeComments(self, rawlines: List[str]) -> str:
        """Remove comment portions from lines and join into single string.
        
        Removes any portion of each line that follows a '#' symbol.
        
        Args:
            rawlines: List of raw input lines
            
        Returns:
            String with all lines joined, with comments removed
        """
        fixed_lines = []
        for l in rawlines:
            idx = l.find("#")
            if idx == -1:
                fixed_lines.append(l)
            else:
                fixed_lines.append(l[0:idx])
        return "\n".join(fixed_lines)

    def parse(self) -> Dict[str, Any]:
        """Parse test file into dictionary of test data.
        
        Reads test file, removes comments, and parses into a dictionary containing
        test properties and metadata. Handles both single-line and multi-line
        property values.
        
        Returns:
            Dictionary containing parsed test data and metadata
        """
        test = {}
        print(self.path)
        with open(self.path) as handle:
            raw_lines = handle.read().split("\n")

        test_text = self.removeComments(raw_lines)
        test["__raw_lines__"] = raw_lines
        test["path"] = self.path
        test["__emit__"] = []
        lines = test_text.split("\n")
        i = 0
        # read a property in each loop cycle
        while i < len(lines):
            # skip blank lines
            if re.match(r"\A\s*\Z", lines[i]):
                test["__emit__"].append(("raw", raw_lines[i]))
                i += 1
                continue
            m = re.match(r'\A([^"]*?):\s*"([^"]*)"\s*\Z', lines[i])
            if m:
                test[m.group(1)] = m.group(2)
                test["__emit__"].append(("oneline", m.group(1)))
                i += 1
                continue
            m = re.match(r'\A([^"]*?):\s*"""\s*\Z', lines[i])
            if m:
                msg = []
                i += 1
                while not re.match(r'\A\s*"""\s*\Z', lines[i]):
                    msg.append(raw_lines[i])
                    i += 1
                test[m.group(1)] = "\n".join(msg)
                test["__emit__"].append(("multiline", m.group(1)))
                i += 1
                continue
            print(f"error parsing test file: {self.path}")
            sys.exit(1)
        return test


def emitTestDict(testDict: Dict[str, Any], handle: Any) -> None:
    """Write test dictionary back to file handle.
    
    Args:
        testDict: Dictionary containing test data to write
        handle: File handle to write to
    """
    for kind, data in testDict["__emit__"]:
        if kind == "raw":
            handle.write(f"{data}\n")
        elif kind == "oneline":
            handle.write(f'{data}: "{testDict[data]}"\n')
        elif kind == "multiline":
            handle.write(f'{data}: """\n{testDict[data]}\n"""\n')
        else:
            raise Exception("Bad __emit__")
