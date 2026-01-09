"""Common code for autograders and grading utilities.

This module provides grading functionality for autograding student projects,
including tracking scores, providing feedback, and generating formatted output
in various formats (edX, GradeScope).

Original Authors:
    John DeNero (denero@cs.berkeley.edu)
    Dan Klein (klein@cs.berkeley.edu)
    Brad Miller
    Nick Hay
    Pieter Abbeel (pabbeel@cs.berkeley.edu)

Modified by:
    George Rudolph
    Date: 9 Nov 2024

Changes:
    - Added type hints throughout
    - Improved docstrings and documentation
    - Reorganized imports
    - Verified to run with Python 3.13

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

import html
import time
import sys
import json
import traceback
import pdb
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple, Any

import util

class Grades:
    """
    A data structure for project grades, along with formatting code to display them.
    
    Attributes:
        questions (List[str]): List of question names
        maxes (Dict[str, int]): Maximum points possible for each question
        points (Counter): Points earned for each question
        messages (Dict[str, List[str]]): Messages/feedback for each question
        project (str): Name of the project
        start (Tuple[int, int, int, int, int]): Start time tuple (month,day,hour,min,sec)
        sane (bool): Whether sanity checks have passed
        currentQuestion (Optional[str]): Question currently being graded
        edxOutput (bool): Whether to output edX format
        gsOutput (bool): Whether to output GradeScope format
        mute (bool): Whether to mute output
        prereqs (DefaultDict[str, Set[str]]): Prerequisites for each question
    """
    def __init__(self, projectName: str, questionsAndMaxesList: List[tuple[str, int]],
                 gsOutput: bool = False, edxOutput: bool = False, muteOutput: bool = False) -> None:
        """
        Initialize the grading scheme for a project.
        
        Args:
            projectName: Name of the project
            questionsAndMaxesList: List of (question name, max points) tuples
            gsOutput: Whether to output in GradeScope format
            edxOutput: Whether to output in edX format
            muteOutput: Whether to mute output
        """
        self.questions = [el[0] for el in questionsAndMaxesList]
        self.maxes = dict(questionsAndMaxesList)
        self.points = Counter()
        self.messages = {q: [] for q in self.questions}
        self.project = projectName
        self.start = time.localtime()[1:6]
        self.sane = True  # Sanity checks
        self.currentQuestion = None  # Which question we're grading
        self.edxOutput = edxOutput
        self.gsOutput = gsOutput  # GradeScope output
        self.mute = muteOutput
        self.prereqs = defaultdict(set)

        print(f'Starting on {self.start[0]}-{self.start[1]} at {self.start[2]}:{self.start[3]:02d}:{self.start[4]:02d}')

    def addPrereq(self, question: str, prereq: str) -> None:
        """Add a prerequisite question that must be completed first."""
        self.prereqs[question].add(prereq)

    def grade(self, gradingModule: Any, exceptionMap: dict = {}, bonusPic: bool = False) -> None:
        """
        Grade each question using the provided grading module.
        
        Args:
            gradingModule: Module containing grading functions
            exceptionMap: Map of exceptions to helpful messages
            bonusPic: Whether to show bonus picture for perfect score
        """
        completedQuestions = set()
        for q in self.questions:
            print(f'\nQuestion {q}')
            print('=' * (9 + len(q)))
            print()
            self.currentQuestion = q

            incompleted = self.prereqs[q].difference(completedQuestions)
            if len(incompleted) > 0:
                prereq = incompleted.pop()
                print(
f"""*** NOTE: Make sure to complete Question {prereq} before working on Question {q},
*** because Question {q} builds upon your answer for Question {prereq}.
""")
                continue

            if self.mute: util.mutePrint()
            try:
                util.TimeoutFunction(getattr(gradingModule, q),1800)(self)  # Call the question's function
            except Exception as inst:
                self.addExceptionMessage(q, inst, traceback)
                self.addErrorHints(exceptionMap, inst, q[1])
            except:
                self.fail('FAIL: Terminated with a string exception.')
            finally:
                if self.mute: util.unmutePrint()

            if self.points[q] >= self.maxes[q]:
                completedQuestions.add(q)

            print(f'\n### Question {q}: {self.points[q]}/{self.maxes[q]} ###\n')

        print(f'\nFinished at {time.localtime()[3]:d}:{time.localtime()[4]:02d}:{time.localtime()[5]:02d}')
        print("\nProvisional grades\n==================")

        for q in self.questions:
            print(f'Question {q}: {self.points[q]}/{self.maxes[q]}')
        print('------------------')
        print(f'Total: {self.points.totalCount()}/{sum(self.maxes.values())}')

        if bonusPic and self.points.totalCount() == 25:
            print("""

                     ALL HAIL GRANDPAC.
              LONG LIVE THE GHOSTBUSTING KING.

                  ---      ----      ---
                  |  \    /  + \    /  |
                  | + \--/      \--/ + |
                  |   +     +          |
                  | +     +        +   |
                @@@@@@@@@@@@@@@@@@@@@@@@@@
              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            \   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
             \ /  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
              V   \   @@@@@@@@@@@@@@@@@@@@@@@@@@@@
                   \ /  @@@@@@@@@@@@@@@@@@@@@@@@@@
                    V     @@@@@@@@@@@@@@@@@@@@@@@@
                            @@@@@@@@@@@@@@@@@@@@@@
                    /\      @@@@@@@@@@@@@@@@@@@@@@
                   /  \  @@@@@@@@@@@@@@@@@@@@@@@@@
              /\  /    @@@@@@@@@@@@@@@@@@@@@@@@@@@
             /  \ @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            /    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                @@@@@@@@@@@@@@@@@@@@@@@@@@
                    @@@@@@@@@@@@@@@@@@

""")
        print("""
Your grades are NOT yet registered.  To register your grades, make sure
to follow your instructor's guidelines to receive credit on your project.
""")

        if self.edxOutput:
            self.produceOutput()
        if self.gsOutput:
            self.produceGradeScopeOutput()

    def addExceptionMessage(self, q: str, inst: Exception, traceback: Any) -> None:
        """
        Format and add exception message to question feedback.
        
        Args:
            q: Question name
            inst: Exception instance
            traceback: Traceback object
        """
        self.fail(f'FAIL: Exception raised: {inst}')
        self.addMessage('')
        for line in traceback.format_exc().split('\n'):
            self.addMessage(line)

    def addErrorHints(self, exceptionMap: dict, errorInstance: Exception, questionNum: str) -> None:
        """
        Add helpful error hints based on the type of exception.
        
        Args:
            exceptionMap: Map of exceptions to helpful messages
            errorInstance: The exception that was raised
            questionNum: Question number
        """
        typeOf = str(type(errorInstance))
        questionName = 'q' + questionNum
        errorHint = ''

        # Question specific error hints
        if exceptionMap.get(questionName):
            questionMap = exceptionMap.get(questionName)
            if questionMap.get(typeOf):
                errorHint = questionMap.get(typeOf)
        # Fall back to general error messages
        if exceptionMap.get(typeOf):
            errorHint = exceptionMap.get(typeOf)

        if not errorHint:
            return

        for line in errorHint.split('\n'):
            self.addMessage(line)

    def produceGradeScopeOutput(self) -> None:
        """Generate output file in GradeScope format."""
        out_dct = {}

        # Total of entire submission
        total_possible = sum(self.maxes.values())
        total_score = sum(self.points.values())
        out_dct['score'] = total_score
        out_dct['max_score'] = total_possible
        out_dct['output'] = f"Total score ({total_score} / {total_possible})"

        # Individual tests
        tests_out = []
        for name in self.questions:
            test_out = {}
            test_out['name'] = name
            test_out['score'] = self.points[name]
            test_out['max_score'] = self.maxes[name]
            
            is_correct = self.points[name] >= self.maxes[name]
            test_out['output'] = f"  Question {name[1] if len(name) == 2 else name} ({test_out['score']}/{test_out['max_score']}) {'X' if not is_correct else ''}"
            test_out['tags'] = []
            tests_out.append(test_out)
        out_dct['tests'] = tests_out

        with open('gradescope_response.json', 'w') as outfile:
            json.dump(out_dct, outfile)

    def produceOutput(self) -> None:
        """Generate output file in edX format."""
        edxOutput = open('edx_response.html', 'w')
        edxOutput.write("<div>")

        total_possible = sum(self.maxes.values())
        total_score = sum(self.points.values())
        checkOrX = '<span class="correct"/>' if total_score >= total_possible else '<span class="incorrect"/>'
        
        header = f"""
        <h3>
            Total score ({total_score} / {total_possible})
        </h3>
        """
        edxOutput.write(header)

        for q in self.questions:
            name = q[1] if len(q) == 2 else q
            checkOrX = '<span class="correct"/>' if self.points[q] >= self.maxes[q] else '<span class="incorrect"/>'
            messages = f"<pre>{chr(10).join(self.messages[q])}</pre>"
            
            output = f"""
        <div class="test">
          <section>
          <div class="shortform">
            Question {name} ({self.points[q]}/{self.maxes[q]}) {checkOrX}
          </div>
        <div class="longform">
          {messages}
        </div>
        </section>
      </div>
      """
            edxOutput.write(output)
            
        edxOutput.write("</div>")
        edxOutput.close()
        
        with open('edx_grade', 'w') as edxOutput:
            edxOutput.write(str(self.points.totalCount()))

    def fail(self, message: str, raw: bool = False) -> None:
        """
        Set sanity check to false and output failure message.
        
        Args:
            message: Failure message
            raw: Whether message is pre-formatted HTML
        """
        self.sane = False
        self.assignZeroCredit()
        self.addMessage(message, raw)

    def assignZeroCredit(self) -> None:
        """Assign zero points to current question."""
        self.points[self.currentQuestion] = 0

    def addPoints(self, amt: int) -> None:
        """Add points to current question score."""
        self.points[self.currentQuestion] += amt

    def deductPoints(self, amt: int) -> None:
        """Deduct points from current question score."""
        self.points[self.currentQuestion] -= amt

    def assignFullCredit(self, message: str = "", raw: bool = False) -> None:
        """
        Assign maximum points to current question.
        
        Args:
            message: Optional message to display
            raw: Whether message is pre-formatted HTML
        """
        self.points[self.currentQuestion] = self.maxes[self.currentQuestion]
        if message:
            self.addMessage(message, raw)

    def addMessage(self, message: str, raw: bool = False) -> None:
        """
        Add a message to the current question's feedback.
        
        Args:
            message: Message to add
            raw: Whether message is pre-formatted HTML
        """
        if not raw:
            if self.mute: util.unmutePrint()
            print('*** ' + message)
            if self.mute: util.mutePrint()
            message = html.escape(message)
        self.messages[self.currentQuestion].append(message)

    def addMessageToEmail(self, message: str) -> None:
        """Deprecated method for adding messages to email."""
        print(f"WARNING**** addMessageToEmail is deprecated {message}")

class Counter(dict):
    """
    A dictionary subclass that returns 0 for missing keys.
    
    This class extends dict to provide a default value of 0 for any key that
    doesn't exist, making it useful for counting occurrences.
    """
    def __getitem__(self, idx: str) -> int:
        """
        Get the count for a key, returning 0 if the key doesn't exist.
        
        Args:
            idx: The key to look up
            
        Returns:
            The count for the key, or 0 if not found
        """
        try:
            return dict.__getitem__(self, idx)
        except KeyError:
            return 0

    def totalCount(self) -> int:
        """
        Calculate the sum of all counts in the Counter.
        
        Returns:
            The total sum of all values in the Counter
        """
        return sum(self.values())
