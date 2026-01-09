"""
Common code for autograders.

This module provides functionality for grading student project submissions using a flexible
and extensible framework. It handles:
- Tracking points and messages for each question
- Handling timeouts and exceptions during grading
- Generating formatted output for different platforms (edX, GradeScope)
- Supporting prerequisite relationships between questions
- Customizable grading schemes and point allocations
- Detailed feedback generation for students
- Progress tracking and timing information
- Exception handling and error reporting

The main class is Grades which manages the grading process and output generation.
The grading framework is highly configurable with options for:
- Multiple output formats (edX, GradeScope)
- Custom scoring schemes
- Prerequisite relationships
- Timeout handling
- Detailed vs summary feedback
- Platform-specific formatting

Most code originally by Dan Klein and John Denero for CS188 at UC Berkeley.
Some code from LiveWires Pacman implementation, used with permission.

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added type hints throughout module
- Added detailed grading configuration options
- Added Python version compatibility note
- Added last modified date and modifier
- Verified Python 3.13 compatibility

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

import html
import time
import sys
import json
import traceback
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Any, Optional
import util


class Grades:
    """
    A data structure for project grades, along with formatting code to display them.
    
    Tracks points earned, messages, and prerequisites for each question in a project.
    Can generate formatted output for different platforms like edX and GradeScope.
    """

    def __init__(self, projectName: str, questionsAndMaxesList: List[Tuple[str, int]],
                 gsOutput: bool = False, edxOutput: bool = False, muteOutput: bool = False) -> None:
        """
        Initialize the grading scheme for a project.

        Args:
            projectName: Name of the project being graded
            questionsAndMaxesList: List of (question name, max points) tuples
            gsOutput: Whether to generate GradeScope formatted output
            edxOutput: Whether to generate edX formatted output 
            muteOutput: Whether to suppress printing during grading
        """
        self.questions = [el[0] for el in questionsAndMaxesList]
        self.maxes = dict(questionsAndMaxesList)
        self.points = Counter()
        self.messages = dict([(q, []) for q in self.questions])
        self.project = projectName
        self.start = time.localtime()[1:6]
        self.sane = True  # Sanity checks
        self.currentQuestion: Optional[str] = None  # Which question we're grading
        self.edxOutput = edxOutput
        self.gsOutput = gsOutput  # GradeScope output
        self.mute = muteOutput
        self.prereqs: Dict[str, Set[str]] = defaultdict(set)

        print(f'Starting on {self.start[0]}-{self.start[1]} at {self.start[2]}:{self.start[3]:02d}:{self.start[4]:02d}')

    def addPrereq(self, question: str, prereq: str) -> None:
        """Add a prerequisite relationship between questions."""
        self.prereqs[question].add(prereq)

    def grade(self, gradingModule: Any, exceptionMap: Dict[str, Any] = {}, bonusPic: bool = False) -> None:
        """
        Grade each question in the project.

        Args:
            gradingModule: Module containing grading functions (pass in with sys.modules[__name__])
            exceptionMap: Mapping of exceptions to helpful error messages
            bonusPic: Whether to display bonus ASCII art for perfect score
        """

        completedQuestions = set([])
        for q in self.questions:
            print('\nQuestion %s' % q)
            print('=' * (9 + len(q)))
            print()
            self.currentQuestion = q

            incompleted = self.prereqs[q].difference(completedQuestions)
            if len(incompleted) > 0:
                prereq = incompleted.pop()
                print(f"""*** NOTE: Make sure to complete Question {prereq} before working on Question {q},
*** because Question {q} builds upon your answer for Question {prereq}.
""")
                continue

            if self.mute:
                util.mutePrint()
            try:
                util.TimeoutFunction(getattr(gradingModule, q), 1800)(
                    self)  # Call the question's function
                # TimeoutFunction(getattr(gradingModule, q),1200)(self) # Call the question's function
            except Exception as inst:
                self.addExceptionMessage(q, inst, traceback)
                self.addErrorHints(exceptionMap, inst, q[1])
            except:
                self.fail('FAIL: Terminated with a string exception.')
            finally:
                if self.mute:
                    util.unmutePrint()

            if self.points[q] >= self.maxes[q]:
                completedQuestions.add(q)

            print(f'\n### Question {q}: {self.points[q]}/{self.maxes[q]} ###\n')

        print(f'\nFinished at {time.localtime()[3]}:{time.localtime()[4]:02d}:{time.localtime()[5]:02d}')
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
        Format and add exception message to question output.
        
        Args:
            q: Question name
            inst: Exception instance
            traceback: Traceback object
        """
        self.fail(f'FAIL: Exception raised: {inst}')
        self.addMessage('')
        for line in traceback.format_exc().split('\n'):
            self.addMessage(line)

    def addErrorHints(self, exceptionMap: Dict[str, Any], errorInstance: Exception, questionNum: str) -> None:
        """
        Add any error hints based on the exception type and question.
        
        Args:
            exceptionMap: Mapping of exceptions to hint messages
            errorInstance: The exception that was raised
            questionNum: Question number as string
        """
        typeOf = str(type(errorInstance))
        questionName = 'q' + questionNum
        errorHint = ''

        # question specific error hints
        if exceptionMap.get(questionName):
            questionMap = exceptionMap.get(questionName)
            if (questionMap.get(typeOf)):
                errorHint = questionMap.get(typeOf)
        # fall back to general error messages if a question specific
        # one does not exist
        if (exceptionMap.get(typeOf)):
            errorHint = exceptionMap.get(typeOf)

        # dont include the HTML if we have no error hint
        if not errorHint:
            return ''

        for line in errorHint.split('\n'):
            self.addMessage(line)

    def produceGradeScopeOutput(self) -> None:
        """Generate output file formatted for GradeScope."""
        out_dct = {}

        # total of entire submission
        total_possible = sum(self.maxes.values())
        total_score = sum(self.points.values())
        out_dct['score'] = total_score
        out_dct['max_score'] = total_possible
        out_dct['output'] = f"Total score ({total_score} / {total_possible})"

        # individual tests
        tests_out = []
        for name in self.questions:
            test_out = {}
            # test name
            test_out['name'] = name
            # test score
            test_out['score'] = self.points[name]
            test_out['max_score'] = self.maxes[name]
            # others
            is_correct = self.points[name] >= self.maxes[name]
            test_out['output'] = f"  Question {name[1] if len(name) == 2 else name} ({test_out['score']}/{test_out['max_score']}) {'X' if not is_correct else ''}"
            test_out['tags'] = []
            tests_out.append(test_out)
        out_dct['tests'] = tests_out

        # file output
        with open('gradescope_response.json', 'w') as outfile:
            json.dump(out_dct, outfile)
        return

    def produceOutput(self) -> None:
        """Generate output file formatted for edX."""
        edxOutput = open('edx_response.html', 'w')
        edxOutput.write("<div>")

        # first sum
        total_possible = sum(self.maxes.values())
        total_score = sum(self.points.values())
        checkOrX = '<span class="incorrect"/>'
        if (total_score >= total_possible):
            checkOrX = '<span class="correct"/>'
        header = f"""
        <h3>
            Total score ({total_score} / {total_possible})
        </h3>
    """
        edxOutput.write(header)

        for q in self.questions:
            if len(q) == 2:
                name = q[1]
            else:
                name = q
            checkOrX = '<span class="incorrect"/>'
            if (self.points[q] >= self.maxes[q]):
                checkOrX = '<span class="correct"/>'
            #messages = '\n<br/>\n'.join(self.messages[q])
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
            # print "*** output for Question %s " % q[1]
            # print output
            edxOutput.write(output)
        edxOutput.write("</div>")
        edxOutput.close()
        edxOutput = open('edx_grade', 'w')
        edxOutput.write(str(self.points.totalCount()))
        edxOutput.close()

    def fail(self, message: str, raw: bool = False) -> None:
        """
        Set sanity check bit to false and output a message.
        
        Args:
            message: Message to display
            raw: Whether message is pre-formatted HTML
        """
        self.sane = False
        self.assignZeroCredit()
        self.addMessage(message, raw)

    def assignZeroCredit(self) -> None:
        """Set points for current question to zero."""
        self.points[self.currentQuestion] = 0

    def addPoints(self, amt: int) -> None:
        """Add points to current question score."""
        self.points[self.currentQuestion] += amt

    def deductPoints(self, amt: int) -> None:
        """Deduct points from current question score."""
        self.points[self.currentQuestion] -= amt

    def assignFullCredit(self, message: str = "", raw: bool = False) -> None:
        """
        Assign maximum points for current question.
        
        Args:
            message: Optional message to display
            raw: Whether message is pre-formatted HTML
        """
        self.points[self.currentQuestion] = self.maxes[self.currentQuestion]
        if message != "":
            self.addMessage(message, raw)

    def addMessage(self, message: str, raw: bool = False) -> None:
        """
        Add a message to the current question's output.
        
        Args:
            message: Message to add
            raw: Whether message is pre-formatted HTML
        """
        if not raw:
                # We assume raw messages, formatted for HTML, are printed separately
            if self.mute:
                util.unmutePrint()
            print('*** ' + message)
            if self.mute:
                util.mutePrint()
            message = html.escape(message)
        self.messages[self.currentQuestion].append(message)

    def addMessageToEmail(self, message: str) -> None:
        """
        DEPRECATED: Add a message to be emailed.
        
        Args:
            message: Message to add
        """
        print(f"WARNING**** addMessageToEmail is deprecated {message}")
        for line in message.split('\n'):
            pass
            # print '%%% ' + line + ' %%%'
            # self.messages[self.currentQuestion].append(line)


class Counter(dict):
    """
    Dict with default value of 0 for missing keys.
    Used for tracking points per question.
    """

    def __getitem__(self, idx: str) -> int:
        """Get count for key, returning 0 if not found."""
        try:
            return dict.__getitem__(self, idx)
        except KeyError:
            return 0

    def totalCount(self) -> int:
        """Return sum of counts for all keys."""
        return sum(self.values())
