# tracking_fa14TestClasses.py
# ---------------------------
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


# tracking_fa14TestClasses.py
# ---------------------------
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


# trackingTestClasses.py
# ----------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and Pieter
# Abbeel in Spring 2013.
# For more info, see http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html

import testClasses
import busters
import layout
import bustersAgents
from game import Agent
from game import Actions
from game import Directions
import random
import time
import util
import json
import re
import copy
from util import manhattanDistance
from typing import List, Dict, Any, Optional, Tuple, Union

fixed_order = ["West", "East", "Stop", "South", "North"]


class GameScoreTest(testClasses.TestCase):
    """Test case that runs a game and checks for minimum score threshold across multiple runs.
    
    Tests if a Pacman agent can achieve a minimum score threshold over multiple games
    by running the game multiple times and tracking performance statistics.
    """

    def __init__(self, question: Any, testDict: Dict[str, Any]) -> None:
        """Initialize the game score test.

        Args:
            question: The test question object
            testDict: Dictionary containing test parameters including:
                maxMoves: Maximum moves allowed per game
                inference: Type of inference module to use
                layout_str: String representation of game layout
                numRuns: Number of games to run
                numWinsForCredit: Number of wins needed to pass
                numGhosts: Number of ghost agents
                layout_name: Name of the layout being tested
                min_score: Minimum score threshold
                observe: Whether observation is enabled
                elapse: Whether time elapsing is enabled
        """
        super(GameScoreTest, self).__init__(question, testDict)
        self.maxMoves = int(self.testDict["maxMoves"])
        self.inference = self.testDict["inference"]
        self.layout_str = self.testDict["layout_str"].split("\n")
        self.numRuns = int(self.testDict["numRuns"])
        self.numWinsForCredit = int(self.testDict["numWinsForCredit"])
        self.numGhosts = int(self.testDict["numGhosts"])
        self.layout_name = self.testDict["layout_name"]
        self.min_score = int(self.testDict["min_score"])
        self.observe_enable = self.testDict["observe"] == "True"
        self.elapse_enable = self.testDict["elapse"] == "True"

    def execute(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        """Execute the game score test case.
        
        Runs multiple games with a GreedyBustersAgent and checks if enough games achieve 
        the minimum score threshold. Creates ghost agents, sets up the Pacman agent with
        the specified inference type, and runs the games while tracking scores.

        Args:
            grades: The grading object
            moduleDict: Dictionary containing student modules
            solutionDict: Dictionary containing solution data

        Returns:
            bool: True if enough games exceed minimum score threshold, False otherwise
        """
        ghosts = [SeededRandomGhostAgent(i) for i in range(1, self.numGhosts + 1)]
        print(self.inference)
        pac = bustersAgents.GreedyBustersAgent(
            0,
            inference=self.inference,
            ghostAgents=ghosts,
            observeEnable=self.observe_enable,
            elapseTimeEnable=self.elapse_enable,
        )
        # if self.inference == "ExactInference":
        #    pac.inferenceModules = [moduleDict['inference'].ExactInference(a) for a in ghosts]
        # else:
        #    print "Error inference type %s -- not implemented" % self.inference
        #    return

        stats = run(
            self.layout_str,
            pac,
            ghosts,
            self.question.getDisplay(),
            nGames=self.numRuns,
            maxMoves=self.maxMoves,
            quiet=False,
        )
        aboveCount = [s >= self.min_score for s in stats["scores"]].count(True)
        msg = f"{self.layout_name}) Games won on {grades.currentQuestion} with score above {self.min_score}: {aboveCount}/{self.numRuns}"
        grades.addMessage(msg)
        if aboveCount >= self.numWinsForCredit:
            grades.assignFullCredit()
            return self.testPass(grades)
        else:
            return self.testFail(grades)
    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> None:
        handle = open(filePath, "w")
        handle.write(
            f"# You must win at least {self.numWinsForCredit}/10 games with at least {self.min_score} points"
        )
        handle.close()

    def createPublicVersion(self) -> None:
        pass


class ZeroWeightTest(testClasses.TestCase):
    """Test case that checks handling of zero weight particles.
    
    Tests if the particle filter implementation correctly handles the case when
    all particle weights become zero by checking if weights get reset.
    """

    def __init__(self, question: Any, testDict: Dict[str, Any]) -> None:
        """Initialize the zero weight test.

        Args:
            question: The test question object
            testDict: Dictionary containing test parameters including:
                maxMoves: Maximum moves allowed per game
                inference: Type of inference module to use
                layout: String representation of game layout
                numGhosts: Number of ghost agents
                observe: Whether observation is enabled
                elapse: Whether time elapsing is enabled
                ghost: Type of ghost agent to use
                seed: Random seed for reproducibility
        """
        super(ZeroWeightTest, self).__init__(question, testDict)
        self.maxMoves = int(self.testDict["maxMoves"])
        self.inference = self.testDict["inference"]
        self.layout_str = self.testDict["layout"].split("\n")
        self.numGhosts = int(self.testDict["numGhosts"])
        self.observe_enable = self.testDict["observe"] == "True"
        self.elapse_enable = self.testDict["elapse"] == "True"
        self.ghost = self.testDict["ghost"]
        self.seed = int(self.testDict["seed"])

    def execute(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        random.seed(self.seed)
        inferenceFunction = getattr(moduleDict["inference"], self.inference)
        ghosts = [globals()[self.ghost](i) for i in range(1, self.numGhosts + 1)]
        if self.inference == "MarginalInference":
            moduleDict["inference"].jointInference = moduleDict[
                "inference"
            ].JointParticleFilter()
        disp = self.question.getDisplay()
        pac = ZeroWeightAgent(
            inferenceFunction,
            ghosts,
            grades,
            self.seed,
            disp,
            elapse=self.elapse_enable,
            observe=self.observe_enable,
        )
        if self.inference == "ParticleFilter":
            for pfilter in pac.inferenceModules:
                pfilter.setNumParticles(5000)
        elif self.inference == "MarginalInference":
            moduleDict["inference"].jointInference.setNumParticles(5000)
        run(self.layout_str, pac, ghosts, disp, maxMoves=self.maxMoves)
        if pac.getReset():
            grades.addMessage(
                f"{grades.currentQuestion}) successfully handled all weights = 0"
            )
            return self.testPass(grades)
        else:
            grades.addMessage(
                f"{grades.currentQuestion}) error handling all weights = 0"
            )
            return self.testFail(grades)

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> None:
        handle = open(filePath, "w")
        handle.write(
            "# This test checks that you successfully handle the case when all particle weights are set to 0\n"
        )
        handle.close()

    def createPublicVersion(self) -> None:
        self.testDict["seed"] = "188"
        self.seed = 188


class DoubleInferenceAgentTest(testClasses.TestCase):
    """Test case that compares inference distributions against reference distributions.
    
    Tests if a student's inference implementation matches the reference implementation
    by comparing belief distributions within specified tolerances.
    """

    def __init__(self, question: Any, testDict: Dict[str, Any]) -> None:
        """Initialize the double inference test.

        Args:
            question: The test question object
            testDict: Dictionary containing test parameters including:
                seed: Random seed for reproducibility
                layout: String representation of game layout
                observe: Whether observation is enabled
                elapse: Whether time elapsing is enabled
                checkUniform: Whether to check for uniform distributions
                maxMoves: Maximum moves allowed per game
                numGhosts: Number of ghost agents
                inference: Type of inference module to use
                errorMsg: Error message template
                L2Tolerance: L2 norm tolerance for distribution comparison
                ghost: Type of ghost agent to use
        """
        super(DoubleInferenceAgentTest, self).__init__(question, testDict)
        self.seed = int(self.testDict["seed"])
        self.layout_str = self.testDict["layout"].split("\n")
        self.observe = self.testDict["observe"] == "True"
        self.elapse = self.testDict["elapse"] == "True"
        self.checkUniform = self.testDict["checkUniform"] == "True"
        self.maxMoves = int(self.testDict["maxMoves"])
        self.numGhosts = int(self.testDict["numGhosts"])
        self.inference = self.testDict["inference"]
        self.errorMsg = self.testDict["errorMsg"]
        self.L2Tolerance = float(self.testDict["L2Tolerance"])
        self.ghost = self.testDict["ghost"]

    def execute(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        random.seed(self.seed)
        lines = solutionDict["correctActions"].split("\n")
        moves = []
        # Collect solutions
        for l in lines:
            m = re.match("(\d+) (\w+) (.*)", l)
            moves.append((m.group(1), m.group(2), eval(m.group(3))))

        inferenceFunction = getattr(moduleDict["inference"], self.inference)

        ghosts = [globals()[self.ghost](i) for i in range(1, self.numGhosts + 1)]
        if self.inference == "MarginalInference":
            moduleDict["inference"].jointInference = moduleDict[
                "inference"
            ].JointParticleFilter()

        disp = self.question.getDisplay()
        pac = DoubleInferenceAgent(
            inferenceFunction,
            moves,
            ghosts,
            grades,
            self.seed,
            disp,
            self.inference,
            elapse=self.elapse,
            observe=self.observe,
            L2Tolerance=self.L2Tolerance,
            checkUniform=self.checkUniform,
        )
        if self.inference == "ParticleFilter":
            for pfilter in pac.inferenceModules:
                pfilter.setNumParticles(5000)
        elif self.inference == "MarginalInference":
            moduleDict["inference"].jointInference.setNumParticles(5000)
        run(self.layout_str, pac, ghosts, disp, maxMoves=self.maxMoves)
        msg = self.errorMsg % pac.errors
        grades.addMessage(f"{grades.currentQuestion}) {msg}")
        if pac.errors == 0:
            grades.addPoints(2)
            return self.testPass(grades)
        else:
            return self.testFail(grades)

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> None:
        random.seed(self.seed)
        if self.inference == "ParticleFilter":
            self.inference = (
                "ExactInference"  # use exact inference to generate solution
            )
        inferenceFunction = getattr(moduleDict["inference"], self.inference)

        ghosts = [globals()[self.ghost](i) for i in range(1, self.numGhosts + 1)]
        if self.inference == "MarginalInference":
            moduleDict["inference"].jointInference = moduleDict[
                "inference"
            ].JointParticleFilter()
            moduleDict["inference"].jointInference.setNumParticles(5000)

        pac = InferenceAgent(
            inferenceFunction,
            ghosts,
            self.seed,
            elapse=self.elapse,
            observe=self.observe,
        )
        run(
            self.layout_str,
            pac,
            ghosts,
            self.question.getDisplay(),
            maxMoves=self.maxMoves,
        )
        # run our gold code here and then write it to a solution file
        answerList = pac.answerList
        handle = open(filePath, "w")
        handle.write("# move_number action likelihood_dictionary\n")
        handle.write('correctActions: """\n')
        for (moveNum, move, dists) in answerList:
            handle.write(f"{moveNum} {move} [")
            for dist in dists:
                handle.write("{")
                for key in dist:
                    handle.write(f"{key}: {dist[key]}, ")
                handle.write("}, ")
            handle.write("]\n")
        handle.write('"""\n')
        handle.close()

    def createPublicVersion(self) -> None:
        self.testDict["seed"] = "188"
        self.seed = 188


class OutputTest(testClasses.TestCase):
    """Test case that checks output matches expected string.
    
    Tests if the output from student code matches an expected reference string
    by evaluating code and comparing results.
    """

    def __init__(self, question: Any, testDict: Dict[str, Any]) -> None:
        """Initialize the output test.

        Args:
            question: The test question object
            testDict: Dictionary containing test parameters including:
                preamble: Code to execute before test
                test: Test code to evaluate
                success: Success message
                failure: Failure message
        """
        super(OutputTest, self).__init__(question, testDict)
        self.preamble = compile(
            testDict.get("preamble", ""), f"{self.getPath()}.preamble", "exec"
        )
        self.test = compile(testDict["test"], f"{self.getPath()}.test", "eval")
        self.success = testDict["success"]
        self.failure = testDict["failure"]

    def evalCode(self, moduleDict: Dict[str, Any]) -> Any:
        bindings = dict(moduleDict)
        exec(self.preamble, bindings)
        return eval(self.test, bindings)

    def execute(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        result = self.evalCode(moduleDict)
        result = list(map(lambda x: str(x), result))
        result = " ".join(result)

        if result == solutionDict["result"]:
            grades.addMessage(f"PASS: {self.path}")
            grades.addMessage(f"\t{self.success}")
            return True
        else:
            grades.addMessage(f"FAIL: {self.path}")
            grades.addMessage(f"\t{self.failure}")
            grades.addMessage(f'\tstudent result: "{result}"')
            grades.addMessage(f'\tcorrect result: "{solutionDict["result"]}"')

        return False

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        handle = open(filePath, "w")
        handle.write(f"# This is the solution file for {self.path}.\n")
        handle.write(
            "# The result of evaluating the test must equal the below when cast to a string.\n"
        )
        solution = self.evalCode(moduleDict)
        solution = list(map(lambda x: str(x), solution))
        handle.write(f'result: "{" ".join(solution)}"\n')
        handle.close()
        return True

    def createPublicVersion(self) -> None:
        pass


def run(layout_str: List[str], pac: Agent, ghosts: List[Agent], disp: Any, nGames: int = 1, name: str = "games", maxMoves: int = -1, quiet: bool = True) -> Dict[str, Any]:
    """Runs a few games and outputs their statistics.
    
    Args:
        layout_str: List of strings representing game layout
        pac: Pacman agent
        ghosts: List of ghost agents
        disp: Display object
        nGames: Number of games to run
        name: Name for the games
        maxMoves: Maximum moves allowed per game
        quiet: Whether to suppress output
        
    Returns:
        Dictionary containing game statistics including:
            time: Total time taken
            wins: Number of games won
            games: List of game objects
            scores: List of game scores
    """

    starttime = time.time()
    lay = layout.Layout(layout_str)

    # print '*** Running %s on' % name, layname,'%d time(s).' % nGames
    games = busters.runGames(lay, pac, ghosts, disp, nGames, maxMoves)

    # print '*** Finished running %s on' % name, layname, 'after %d seconds.' % (time.time() - starttime)

    stats = {
        "time": time.time() - starttime,
        "wins": [g.state.isWin() for g in games].count(True),
        "games": games,
        "scores": [g.state.getScore() for g in games],
    }
    statTuple = (stats["wins"], len(games), sum(stats["scores"]) * 1.0 / len(games))
    if not quiet:
        print(f"*** Won {statTuple[0]} out of {statTuple[1]} games. Average score: {statTuple[2]} ***")
    return stats


class InferenceAgent(bustersAgents.BustersAgent):
    """Agent that tracks ghosts and compares to reference inference modules while moving randomly.
    
    This agent uses inference modules to track ghost positions and moves randomly,
    while storing the inference results for comparison with reference implementations.
    """

    def __init__(
        self, inference: Any, ghostAgents: List[Agent], seed: int, elapse: bool = True, observe: bool = True, burnIn: int = 0
    ) -> None:
        """Initialize the inference agent.

        Args:
            inference: Inference module class to use
            ghostAgents: List of ghost agents to track
            seed: Random seed for reproducibility
            elapse: Whether to do time elapse updates
            observe: Whether to do observation updates
            burnIn: Number of moves to ignore before comparing distributions
        """
        self.inferenceModules = [inference(a) for a in ghostAgents]
        self.elapse = elapse
        self.observe = observe
        self.burnIn = burnIn
        self.numMoves = 0
        # self.rand = rand
        # list of tuples (move_num, move, [dist_1, dist_2, ...])
        self.answerList = []
        self.seed = seed

    def final(self, gameState: Any) -> None:
        distributionList = []
        self.numMoves += 1
        for index, inf in enumerate(self.inferenceModules):
            if self.observe:
                inf.observe(gameState)
            self.ghostBeliefs[index] = inf.getBeliefDistribution()
            beliefCopy = copy.deepcopy(self.ghostBeliefs[index])
            distributionList.append(beliefCopy)
        self.answerList.append((self.numMoves, None, distributionList))
        random.seed(self.seed + self.numMoves)

    def registerInitialState(self, gameState: Any) -> None:
        """Initialize beliefs and inference modules.
        
        Args:
            gameState: Initial game state
        """
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [
            inf.getBeliefDistribution() for inf in self.inferenceModules
        ]
        self.firstMove = True
        self.answerList.append((self.numMoves, None, copy.deepcopy(self.ghostBeliefs)))

    def getAction(self, gameState: Any) -> str:
        """Update beliefs and choose an action based on updated beliefs.
        
        Args:
            gameState: Current game state
            
        Returns:
            Selected action as a string
        """
        distributionList = []
        self.numMoves += 1
        for index, inf in enumerate(self.inferenceModules):
            if self.elapse:
                if not self.firstMove:
                    inf.elapseTime(gameState)
            self.firstMove = False
            if self.observe:
                inf.observe(gameState)
            self.ghostBeliefs[index] = inf.getBeliefDistribution()
            beliefCopy = copy.deepcopy(self.ghostBeliefs[index])
            distributionList.append(beliefCopy)
        action = random.choice(
            [a for a in gameState.getLegalPacmanActions() if a != "STOP"]
        )
        self.answerList.append((self.numMoves, action, distributionList))
        random.seed(self.seed + self.numMoves)
        return action


class ZeroWeightAgent(bustersAgents.BustersAgent):
    """Agent that tracks ghosts and compares to reference inference modules while moving randomly.
    
    This agent tracks ghost positions using inference modules and moves randomly,
    while checking if particle weights ever get reset to handle zero weight cases.
    """

    def __init__(
        self, inference: Any, ghostAgents: List[Agent], grades: Any, seed: int, disp: Any, elapse: bool = True, observe: bool = True
    ) -> None:
        """Initialize the zero weight agent.

        Args:
            inference: Inference module class to use
            ghostAgents: List of ghost agents to track
            grades: Grading object
            seed: Random seed for reproducibility
            disp: Display object
            elapse: Whether to do time elapse updates
            observe: Whether to do observation updates
        """
        self.inferenceModules = [inference(a) for a in ghostAgents]
        self.elapse = elapse
        self.observe = observe
        self.grades = grades
        self.numMoves = 0
        self.seed = seed
        self.display = disp
        self.reset = False

    def final(self, gameState: Any) -> None:
        pass

    def registerInitialState(self, gameState: Any) -> None:
        """Initialize beliefs and inference modules.
        
        Args:
            gameState: Initial game state
        """
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [
            inf.getBeliefDistribution() for inf in self.inferenceModules
        ]
        self.firstMove = True

    def getAction(self, gameState: Any) -> str:
        """Update beliefs and choose an action based on updated beliefs.
        
        Args:
            gameState: Current game state
            
        Returns:
            Selected action as a string
        """
        newBeliefs = [None] * len(self.inferenceModules)
        self.numMoves += 1
        for index, inf in enumerate(self.inferenceModules):
            if self.elapse:
                if not self.firstMove:
                    inf.elapseTime(gameState)
            self.firstMove = False
            if self.observe:
                inf.observe(gameState)
            newBeliefs[index] = inf.getBeliefDistribution()
        self.checkReset(newBeliefs, self.ghostBeliefs)
        self.ghostBeliefs = newBeliefs
        self.display.updateDistributions(self.ghostBeliefs)
        random.seed(self.seed + self.numMoves)
        action = random.choice(
            [a for a in gameState.getLegalPacmanActions() if a != "STOP"]
        )
        return action

    def checkReset(self, newBeliefs: List[Any], oldBeliefs: List[Any]) -> None:
        """Check if beliefs were reset due to zero weights.
        
        Args:
            newBeliefs: New belief distributions
            oldBeliefs: Previous belief distributions
        """
        for i in range(len(newBeliefs)):
            newKeys = list(
                filter(lambda x: newBeliefs[i][x] != 0, newBeliefs[i].keys())
            )
            oldKeys = list(
                filter(lambda x: oldBeliefs[i][x] != 0, oldBeliefs[i].keys())
            )
            if len(newKeys) > len(oldKeys):
                self.reset = True

    def getReset(self) -> bool:
        """Get whether beliefs were reset.
        
        Returns:
            True if beliefs were reset, False otherwise
        """
        return self.reset


class DoubleInferenceAgent(bustersAgents.BustersAgent):
    """Agent that tracks ghosts and compares to reference inference modules while moving randomly.
    
    This agent tracks ghost positions using inference modules and compares the results
    to reference distributions while moving randomly.
    """

    def __init__(
        self,
        inference: Any,
        refSolution: List[Any],
        ghostAgents: List[Agent],
        grades: Any,
        seed: int,
        disp: Any,
        func: str,
        elapse: bool = True,
        observe: bool = True,
        L2Tolerance: float = 0.2,
        burnIn: int = 0,
        checkUniform: bool = False,
    ) -> None:
        """Initialize the double inference agent.

        Args:
            inference: Inference module class to use
            refSolution: Reference solution to compare against
            ghostAgents: List of ghost agents to track
            grades: Grading object
            seed: Random seed for reproducibility
            disp: Display object
            func: Name of inference function being tested
            elapse: Whether to do time elapse updates
            observe: Whether to do observation updates
            L2Tolerance: L2 norm tolerance for distribution comparison
            burnIn: Number of moves to ignore before comparing distributions
            checkUniform: Whether to check for uniform distributions
        """
        self.inferenceModules = [inference(a) for a in ghostAgents]
        self.refSolution = refSolution
        self.func = func
        self.elapse = elapse
        self.observe = observe
        self.grades = grades
        self.L2Tolerance = L2Tolerance
        self.errors = 0
        self.burnIn = burnIn
        self.numMoves = 0
        self.seed = seed
        self.display = disp
        self.checkUniform = checkUniform

    def final(self, gameState: Any) -> None:
        self.numMoves += 1
        moveNum, action, dists = self.refSolution[self.numMoves]
        for index, inf in enumerate(self.inferenceModules):
            if self.observe:
                inf.observe(gameState)
            self.ghostBeliefs[index] = inf.getBeliefDistribution()
            if self.numMoves >= self.burnIn:
                self.distCompare(self.ghostBeliefs[index], dists[index])
        self.display.updateDistributions(self.ghostBeliefs)
        random.seed(self.seed + self.numMoves)
        if not self.display.checkNullDisplay():
            time.sleep(3)

    def registerInitialState(self, gameState: Any) -> None:
        """Initialize beliefs and inference modules.
        
        Args:
            gameState: Initial game state
        """
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        moveNum, action, dists = self.refSolution[self.numMoves]
        for index, inf in enumerate(self.inferenceModules):
            self.distCompare(inf.getBeliefDistribution(), dists[index])
        self.ghostBeliefs = [
            inf.getBeliefDistribution() for inf in self.inferenceModules
        ]
        self.firstMove = True

    def getAction(self, gameState: Any) -> str:
        """Update beliefs and choose an action based on updated beliefs.
        
        Args:
            gameState: Current game state
            
        Returns:
            Selected action as a string
        """
        self.numMoves += 1
        moveNum, action, dists = self.refSolution[self.numMoves]
        for index, inf in enumerate(self.inferenceModules):
            if self.elapse:
                if not self.firstMove:
                    inf.elapseTime(gameState)
            self.firstMove = False
            if self.observe:
                inf.observe(gameState)
            self.ghostBeliefs[index] = inf.getBeliefDistribution()
            if self.numMoves >= self.burnIn:
                self.distCompare(self.ghostBeliefs[index], dists[index])
        self.display.updateDistributions(self.ghostBeliefs)
        random.seed(self.seed + self.numMoves)
        return action

    def distCompare(self, dist: Dict[Any, float], refDist: Dict[Any, float]) -> None:
        """Compare two distributions for approximate equality.
        
        Args:
            dist: Student's distribution
            refDist: Reference distribution to compare against
        """
        # copy and prepare distributions
        dist = dist.copy()
        refDist = refDist.copy()
        for key in set(list(refDist.keys()) + list(dist.keys())):
            if not key in dist.keys():
                dist[key] = 0.0
            if not key in refDist.keys():
                refDist[key] = 0.0
        # calculate l2 difference
        if sum(refDist.values()) == 0 and self.func != "ExactInference":
            for key in refDist:
                if key[1] != 1:
                    refDist[key] = 1.0 / float(len(refDist))
        l2 = 0
        for k in refDist.keys():
            l2 += (dist[k] - refDist[k]) ** 2
        if l2 > self.L2Tolerance:
            if self.errors == 0:
                t = (self.grades.currentQuestion, self.numMoves, l2)
                summary = (
                    f"{t[0]}) Distribution deviated at move {t[1]} by {t[2]:.4f} (squared norm) from the correct answer.\n"
                )
                header = "%10s%5s%-25s%-25s\n" % ("key:", "", "student", "reference")
                detail = "\n".join(
                    list(
                        map(
                            lambda x: "%9s:%5s%-25s%-25s"
                            % (x, "", dist[x], refDist[x]),
                            set(list(dist.keys()) + list(refDist.keys())),
                        )
                    )
                )
                print(dist.items())
                print(refDist.items())
                self.grades.fail(f"{summary}{header}{detail}")
            self.errors += 1
        # check for uniform distribution if necessary
        if self.checkUniform:
            if abs(max(dist.values()) - max(refDist.values())) > 0.008:
                if self.errors == 0:
                    self.grades.fail(
                        f"{self.grades.currentQuestion}) Distributions do not have the same max value and are therefore not uniform.\n\tstudent max: {max(dist.values())}\n\treference max: {max(refDist.values())}"
                    )
                    self.errors += 1


class SeededRandomGhostAgent(Agent):
    """Ghost agent that moves randomly but with a deterministic seed"""

    def __init__(self, index: int) -> None:
        self.index = index

    def getAction(self, state: Any) -> str:
        dist = util.Counter()
        for a in state.getLegalActions(self.index):
            dist[a] = 1.0
        dist.normalize()
        if len(dist) == 0:
            return Directions.STOP
        else:
            action = self.sample(dist)
            return action

    def getDistribution(self, state: Any) -> util.Counter:
        dist = util.Counter()
        for a in state.getLegalActions(self.index):
            dist[a] = 1.0
        dist.normalize()
        return dist

    def sample(self, distribution: Union[util.Counter, List[float]], values: Optional[List[str]] = None) -> str:
        if type(distribution) == util.Counter:
            items = [(k, distribution[k]) for k in fixed_order if k in distribution]
            distribution = [i[1] for i in items]
            values = [i[0] for i in items]
        if sum(distribution) != 1:
            distribution = normalize(distribution)
        choice = random.random()
        i, total = 0, distribution[0]
        while choice > total:
            i += 1
            total += distribution[i]
        return values[i]


class GoSouthAgent(Agent):
    """Ghost agent that prefers to move south when possible"""

    def __init__(self, index: int) -> None:
        self.index = index

    def getAction(self, state: Any) -> str:
        dist = util.Counter()
        for a in state.getLegalActions(self.index):
            dist[a] = 1.0
        if Directions.SOUTH in dist.keys():
            dist[Directions.SOUTH] *= 2
        dist.normalize()
        if len(dist) == 0:
            return Directions.STOP
        else:
            action = self.sample(dist)
            return action

    def getDistribution(self, state: Any) -> util.Counter:
        dist = util.Counter()
        for a in state.getLegalActions(self.index):
            dist[a] = 1.0
        if Directions.SOUTH in dist.keys():
            dist[Directions.SOUTH] *= 2
        dist.normalize()
        return dist

    def sample(self, distribution: Union[util.Counter, List[float]], values: Optional[List[str]] = None) -> str:
        if type(distribution) == util.Counter:
            items = [(k, distribution[k]) for k in fixed_order if k in distribution]
            distribution = [i[1] for i in items]
            values = [i[0] for i in items]
        if sum(distribution) != 1:
            distribution = util.normalize(distribution)
        choice = random.random()
        i, total = 0, distribution[0]
        while choice > total:
            i += 1
            total += distribution[i]
        return values[i]


class DispersingSeededGhost(Agent):
    """Ghost agent that tries to spread out from other ghosts with some probability"""

    def __init__(self, index: int, spreadProb: float = 0.5) -> None:
        self.index = index
        self.spreadProb = spreadProb

    def getAction(self, state: Any) -> str:
        dist = self.getDistribution(state)
        if len(dist) == 0:
            return Directions.STOP
        else:
            action = self.sample(dist)
            return action

    def getDistribution(self, state: Any) -> util.Counter:
        ghostState = state.getGhostState(self.index)
        legalActions = state.getLegalActions(self.index)
        pos = state.getGhostPosition(self.index)
        isScared = ghostState.scaredTimer > 0

        speed = 1
        if isScared:
            speed = 0.5
        actionVectors = [Actions.directionToVector(a, speed) for a in legalActions]
        newPositions = [(pos[0] + a[0], pos[1] + a[1]) for a in actionVectors]

        # get other ghost positions
        others = [i for i in range(1, state.getNumAgents()) if i != self.index]
        for a in others:
            assert (
                state.getGhostState(a) != None
            ), "Ghost position unspecified in state!"
        otherGhostPositions = [
            state.getGhostPosition(a)
            for a in others
            if state.getGhostPosition(a)[1] > 1
        ]

        # for each action, get the sum of inverse squared distances to the other ghosts
        sumOfDistances = []
        for pos in newPositions:
            sumOfDistances.append(
                sum(
                    [
                        (1 + manhattanDistance(pos, g)) ** (-2)
                        for g in otherGhostPositions
                    ]
                )
            )

        bestDistance = min(sumOfDistances)
        numBest = [bestDistance == dist for dist in sumOfDistances].count(True)
        distribution = util.Counter()
        for action, distance in zip(legalActions, sumOfDistances):
            if distance == bestDistance:
                distribution[action] += self.spreadProb / numBest
            distribution[action] += (1 - self.spreadProb) / len(legalActions)
        return distribution

    def sample(self, distribution, values=None):
        if type(distribution) == util.Counter:
            items = [(k, distribution[k]) for k in fixed_order if k in distribution]
            distribution = [i[1] for i in items]
            values = [i[0] for i in items]
        if sum(distribution) != 1:
            distribution = util.normalize(distribution)
        choice = random.random()
        i, total = 0, distribution[0]
        while choice > total:
            i += 1
            total += distribution[i]
        return values[i]
