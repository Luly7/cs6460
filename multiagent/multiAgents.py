import random
import math
import util
from util import manhattanDistance
from game import Agent, Directions
from typing import List, Tuple, Any
from pacman import GameState


class ReflexAgent(Agent):
    """A reflex agent that chooses actions by examining alternatives via a state evaluation function."""

    def getAction(self, gameState: GameState) -> str:
        """Choose among the best actions according to the evaluation function."""
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(
            gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(
            len(scores)) if scores[index] == bestScore]
        # Pick randomly among the best
        chosenIndex = random.choice(bestIndices)

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action: str) -> float:
        """Evaluate the desirability of a game state after taking an action."""
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [
            ghostState.scaredTimer for ghostState in newGhostStates]

        # ============================================================
        # START ADDED CODE - ReflexAgent Evaluation
        # ============================================================
        # Get the game score
        score = successorGameState.getScore()

        # Set penalty for stopping
        if action == Directions.STOP:
            score -= 10

        # Check distance to ghosts
        for ghostState in newGhostStates:
            g_Pos = ghostState.getPosition()  # Ghost_Position
            g_Dist = manhattanDistance(newPos, g_Pos)  # Ghost Distance

            # If ghost is scared-scored added, otherwise, score decreased
            if ghostState.scaredTimer > 0:
                if g_Dist > 0:
                    score += 100.0 / g_Dist
            else:
                if g_Dist < 2:
                    score -= 500
                elif g_Dist < 4:
                    score -= 100

        # Find distance to nearest food
        food_list = newFood.asList()
        if len(food_list) > 0:
            minFoodDistance = min(
                [manhattanDistance(newPos, food) for food in food_list])
            score += 10.0 / (minFoodDistance + 1)

        # Increase score for finding the food
        if currentGameState.getNumFood() > successorGameState.getNumFood():
            score += 100

        return score
        # ============================================================
        # END ADDED CODE - ReflexAgent Evaluation
        # ============================================================


def scoreEvaluationFunction(currentGameState: GameState) -> float:
    """Return the score of the state for use with adversarial search agents."""
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """Base class for adversarial search agents (minimax, alpha-beta, expectimax)."""

    def __init__(self, evalFn: str = 'scoreEvaluationFunction', depth: str = '2') -> None:
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """Minimax agent that implements adversarial search."""

    def getAction(self, gameState: GameState) -> str:
        """Return the minimax action from the current gameState."""

        # ============================================================
        # START ADDED CODE - Minimax Algorithm
        # ============================================================
        def minimax(state: GameState, depth: int, agentIndex: int) -> Tuple[str, float]:
            """
            Minimax recursive helper function.

            Args:
                state: Current game state
                depth: Current depth (decrements when all agents have moved)
                agentIndex: Current agent (0 = Pacman, 1+ = ghosts)

            Returns:
                Tuple of (best_action, best_value)
            """
            # Base case: terminal state or max depth reached
            if state.isWin() or state.isLose() or depth == 0:
                return None, self.evaluationFunction(state)

            numAgents = state.getNumAgents()
            legalActions = state.getLegalActions(agentIndex)

            # Pacman's turn (MAX)
            if agentIndex == 0:
                best_value = float('-inf')
                best_action = None

                for action in legalActions:
                    successor = state.generateSuccessor(agentIndex, action)
                    _, value = minimax(successor, depth, 1)

                    if value > best_value:
                        best_value = value
                        best_action = action

                return best_action, best_value

            # Ghost's turn (MIN)
            else:
                minValue = float('inf')
                best_action = None

                nextAgent = agentIndex + 1
                nextDepth = depth
                if nextAgent == numAgents:
                    nextAgent = 0
                    nextDepth = depth - 1

                for action in legalActions:
                    successor = state.generateSuccessor(agentIndex, action)
                    _, value = minimax(successor, nextDepth, nextAgent)

                    if value < minValue:
                        minValue = value
                        best_action = action

                return best_action, minValue

        action, _ = minimax(gameState, self.depth, 0)
        return action
        # ============================================================
        # END ADDED CODE - Minimax Algorithm
        # ============================================================


class AlphaBetaAgent(MultiAgentSearchAgent):
    """Minimax agent with alpha-beta pruning optimization."""

    def getAction(self, gameState: GameState) -> str:
        """Return the minimax action using alpha-beta pruning."""

        # ============================================================
        # START ADDED CODE - Alpha-Beta Pruning
        # ============================================================
        def alphaBeta(state: GameState, depth: int, agentIndex: int,
                      alpha: float, beta: float) -> Tuple[str, float]:
            """
            Alpha-beta pruning recursive helper function.

            Args:
                state: Current game state
                depth: Current depth
                agentIndex: Current agent
                alpha: Best value for maximizer along path
                beta: Best value for minimizer along path

            Returns:
                Tuple of (best_action, best_value)
            """
            # Check base case
            if state.isWin() or state.isLose() or depth == 0:
                return None, self.evaluationFunction(state)

            numAgents = state.getNumAgents()
            legalActions = state.getLegalActions(agentIndex)

            # Pacman's turn (MAX)
            if agentIndex == 0:
                best_value = float('-inf')
                best_action = None

                for action in legalActions:
                    successor = state.generateSuccessor(agentIndex, action)
                    _, value = alphaBeta(successor, depth, 1, alpha, beta)

                    if value > best_value:
                        best_value = value
                        best_action = action
                    if value > alpha:
                        alpha = value
                    if alpha > beta:
                        break
                return best_action, best_value

            # Ghost's turn (MIN)
            else:
                minValue = float('inf')
                best_action = None
                nextAgent = agentIndex + 1
                nextDepth = depth

                if nextAgent == numAgents:
                    nextAgent = 0
                    nextDepth = depth - 1

                for action in legalActions:
                    successor = state.generateSuccessor(agentIndex, action)
                    _, value = alphaBeta(
                        successor, nextDepth, nextAgent, alpha, beta)

                    if value < minValue:
                        minValue = value
                        best_action = action
                    if value < beta:
                        beta = value
                    if alpha > beta:
                        break

                return best_action, minValue

        # Start with alpha = -inf, beta = +inf
        action, _ = alphaBeta(gameState, self.depth, 0,
                              float('-inf'), float('inf'))
        return action
        # ============================================================
        # END ADDED CODE - Alpha-Beta Pruning
        # ============================================================


class ExpectimaxAgent(MultiAgentSearchAgent):
    """An agent that uses expectimax search to make decisions."""

    def getAction(self, gameState: GameState) -> str:
        """Return the expectimax action using self.depth and self.evaluationFunction."""

        # ============================================================
        # START ADDED CODE - Expectimax Algorithm
        # ============================================================
        def expectimax(state: GameState, depth: int, agentIndex: int) -> Tuple[str, float]:
            """
            Expectimax recursive helper function.

            Args:
                state: Current game state
                depth: Current depth
                agentIndex: Current agent

            Returns:
                Tuple of (best_action, expected_value)
            """
            # Base case
            if state.isWin() or state.isLose() or depth == 0:
                return None, self.evaluationFunction(state)

            numAgents = state.getNumAgents()
            legalActions = state.getLegalActions(agentIndex)

            # Pacman's turn (MAX)
            if agentIndex == 0:
                best_value = float('-inf')
                best_action = None

                for action in legalActions:
                    successor = state.generateSuccessor(agentIndex, action)
                    _, value = expectimax(successor, depth, 1)

                    if value > best_value:
                        best_value = value
                        best_action = action

                return best_action, best_value

            # Ghost's turn (expectation - probabilistic)
            else:
                expectedValue = 0.0

                nextAgent = agentIndex + 1
                nextDepth = depth

                if nextAgent == numAgents:
                    nextAgent = 0
                    nextDepth = depth - 1

                probability = 1.0 / len(legalActions)

                for action in legalActions:
                    successor = state.generateSuccessor(agentIndex, action)
                    _, value = expectimax(successor, nextDepth, nextAgent)
                    expectedValue += probability * value

                return None, expectedValue

        action, _ = expectimax(gameState, self.depth, 0)
        return action
        # ============================================================
        # END ADDED CODE - Expectimax Algorithm
        # ============================================================


def betterEvaluationFunction(game_state: GameState) -> float:
    """A more sophisticated evaluation function for Pacman game states."""

    # ============================================================
    # START ADDED CODE - UTILITY function
    # ============================================================
    # Get game state information
    pacmanPos = game_state.getPacmanPosition()
    food = game_state.getFood()
    ghostStates = game_state.getGhostStates()
    scaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]
    capsules = game_state.getCapsules()

    # Get with current score
    score = game_state.getScore()

    # Distance to nearest food
    food_list = food.asList()
    if len(food_list) > 0:
        minFoodDistance = min([manhattanDistance(pacmanPos, food)
                              for food in food_list])
        score += 10.0 / (minFoodDistance + 1)
    score -= 4 * len(food_list)

    # Distance to ghosts
    for i, ghostState in enumerate(ghostStates):
        g_Pos = ghostState.getPosition()
        g_Dist = manhattanDistance(pacmanPos, g_Pos)

        if scaredTimes[i] > 0:
            if g_Dist > 0:
                score += 200.0 / g_Dist
            score += 10 * scaredTimes[i]
        else:
            if g_Dist < 3:
                score -= 300 / (g_Dist + 1)
            else:
                score += g_Dist * 2

    # Power capsules-their values is greater when the ghosts are nearby
    if len(capsules) > 0:
        minCapsuleDistance = min(
            [manhattanDistance(pacmanPos, capsule) for capsule in capsules])
        nearbyGhosts = sum(1 for gs in ghostStates
                           if manhattanDistance(pacmanPos, gs.getPosition()) < 5
                           and gs.scaredTimer == 0)
        if nearbyGhosts > 0:
            score += 50.0 / (minCapsuleDistance + 1)
        else:
            score += 10.0 / (minCapsuleDistance + 1)
    score -= 20 * len(capsules)

    return score
    # ============================================================
    # END ADDED CODE - UTILITY function
    # ============================================================


# Abbreviation
better = betterEvaluationFunction
