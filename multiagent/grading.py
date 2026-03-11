"""Grading module for Pacman AI projects.

This module provides grading functionality for the Pacman AI projects, including
question scoring, feedback messages, and output formatting for different platforms.

Modified by: George Rudolph at Utah Valley University
Date: 22 Nov 2024

Updates:
- Added comprehensive docstrings with Args/Returns sections
- Added type hints throughout module
- Improved code organization and readability
- Added constants type annotations
- Added return type hints for all functions
- Added parameter type hints for all functions
- Use f-strings for improved readability
- Python 3.13 compatibility verified

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


"Common code for autograders"

import html
import time
import sys
import json
import traceback
import pdb
from collections import defaultdict
import util


class Grades:
    """
    A data structure for project grades, along with formatting code to display them.
    
    Stores question scores, maximum points, messages, and handles grade output in various formats.
    
    Attributes:
        questions: List of question names/IDs
        maxes: Dict mapping question names to maximum points
        points: Counter tracking points earned per question
        messages: Dict mapping questions to list of feedback messages
        project: Name of the project being graded
        start: Tuple of (month,day,hour,min,sec) when grading started
        sane: Boolean indicating if sanity checks passed
        currentQuestion: Currently active question being graded
        edxOutput: Whether to generate edX formatted output
        gsOutput: Whether to generate GradeScope formatted output
        mute: Whether to suppress print output
        prereqs: Dict mapping questions to their prerequisite questions
    """

    def __init__(self, projectName: str, questionsAndMaxesList: list[tuple[str, int]],
                 gsOutput: bool = False, edxOutput: bool = False, muteOutput: bool = False) -> None:
        """
        Initialize the grading scheme for a project.

        Args:
            projectName: Name of the project
            questionsAndMaxesList: List of (question name, max points) tuples
            gsOutput: Whether to generate GradeScope output
            edxOutput: Whether to generate edX output  
            muteOutput: Whether to suppress print output
        """
        self.questions = [el[0] for el in questionsAndMaxesList]
        self.maxes = dict(questionsAndMaxesList)
        self.points = Counter()
        self.messages = dict([(q, []) for q in self.questions])
        self.project = projectName
        self.start = time.localtime()[1:6]
        self.sane = True  # Sanity checks
        self.currentQuestion = None  # Which question we're grading
        self.edxOutput = edxOutput
        self.gsOutput = gsOutput  # GradeScope output
        self.mute = muteOutput
        self.prereqs = defaultdict(set)

        # print 'Autograder transcript for %s' % self.project
        print(f'Starting on {self.start[0]}-{self.start[1]} at {self.start[2]}:{self.start[3]:02d}:{self.start[4]:02d}')

    def addPrereq(self, question: str, prereq: str) -> None:
        """
        Add a prerequisite question that must be completed before the given question.

        Args:
            question: The question that has a prerequisite
            prereq: The prerequisite question that must be completed first
        """
        self.prereqs[question].add(prereq)

    def grade(self, gradingModule: object, exceptionMap: dict = {}, bonusPic: bool = False) -> None:
        """
        Grade each question using the provided grading module.

        Args:
            gradingModule: Module containing grading functions (pass in with sys.modules[__name__])
            exceptionMap: Dict mapping question names to custom exception handling
            bonusPic: Whether to display bonus ASCII art for perfect score
        """

        completedQuestions = set([])
        for q in self.questions:
            print(f'\nQuestion {q}')
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

    def addExceptionMessage(self, q: str, inst: Exception, traceback: object) -> None:
        """
        Format and add an exception message to the feedback.

        Args:
            q: Question where exception occurred
            inst: The exception instance
            traceback: Traceback object containing stack trace
        """
        self.fail(f'FAIL: Exception raised: {inst}')
        self.addMessage('')
        for line in traceback.format_exc().split('\n'):
            self.addMessage(line)

    def addErrorHints(self, exceptionMap: dict, errorInstance: Exception, questionNum: str) -> None:
        """
        Add custom error hints based on the exception type and question.

        Args:
            exceptionMap: Dict mapping questions/exception types to hint messages
            errorInstance: The exception that was raised
            questionNum: Question number where error occurred
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
        """
        Generate GradeScope-compatible JSON output file with scores and feedback.
        """
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
        """
        Generate edX-compatible HTML output file with scores and feedback.
        """
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
        Set sanity check to false and output failure message.

        Args:
            message: The failure message to display
            raw: Whether message is pre-formatted HTML
        """
        self.sane = False
        self.assignZeroCredit()
        self.addMessage(message, raw)

    def assignZeroCredit(self) -> None:
        """Set score for current question to zero."""
        self.points[self.currentQuestion] = 0

    def addPoints(self, amt: int) -> None:
        """
        Add points to current question score.

        Args:
            amt: Number of points to add
        """
        self.points[self.currentQuestion] += amt

    def deductPoints(self, amt: int) -> None:
        """
        Deduct points from current question score.

        Args:
            amt: Number of points to deduct
        """
        self.points[self.currentQuestion] -= amt

    def assignFullCredit(self, message: str = "", raw: bool = False) -> None:
        """
        Give full credit for current question and optionally add message.

        Args:
            message: Optional message to display
            raw: Whether message is pre-formatted HTML
        """
        self.points[self.currentQuestion] = self.maxes[self.currentQuestion]
        if message != "":
            self.addMessage(message, raw)

    def addMessage(self, message: str, raw: bool = False) -> None:
        """
        Add a message to the feedback for the current question.

        Args:
            message: The message to add
            raw: Whether message is pre-formatted HTML
        """
        if not raw:
                # We assume raw messages, formatted for HTML, are printed separately
            if self.mute:
                util.unmutePrint()
            print(f'*** {message}')
            if self.mute:
                util.mutePrint()
            message = html.escape(message)
        self.messages[self.currentQuestion].append(message)

    def addMessageToEmail(self, message: str) -> None:
        """
        DEPRECATED: Add a message to be emailed to the student.
        
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
    A dictionary subclass that returns 0 for missing keys instead of raising KeyError.
    
    Behaves like a regular dictionary but provides a default value of 0 for any key
    that hasn't been set, making it useful for counting occurrences.
    """

    def __getitem__(self, idx: str) -> int:
        """
        Get the count for a key, returning 0 if the key doesn't exist.
        
        Args:
            idx: The dictionary key to look up
            
        Returns:
            The count value for the key, or 0 if key not found
        """
        try:
            return dict.__getitem__(self, idx)
        except KeyError:
            return 0

    def totalCount(self) -> int:
        """
        Calculate the sum of all counts in the dictionary.
        
        Returns:
            The total sum of all count values stored in the dictionary
        """
        return sum(self.values())
