# AI Usage Reflection Questions

## 1. Which AI did you use?

**Claude Sonnet 4.5** (by Anthropic)
- Accessed through claude.ai web interface
- Used on February 10, 2026
-
## 2. What was your problem/issue?

### Initial Problem:
- **Incomplete code**: Had skeleton code for CS 6460 multi-agent search assignment with five functions containing only `util.raiseNotDefined()` placeholders
- Needed to implement:
  1. `ReflexAgent.evaluationFunction()` - heuristic evaluation
  2. `MinimaxAgent.getAction()` - minimax search
  3. `AlphaBetaAgent.getAction()` - alpha-beta pruning
  4. `ExpectimaxAgent.getAction()` - expectimax search
  5. `betterEvaluationFunction()` - sophisticated state evaluation


## 3. What did you ask it?
Requested a UML diagram to determine the variables required for implementation, along with guidance and assistance in debugging errors related to the failure of the alpha–beta pruning algorithm.


## 4. What was the response?

- AI created a professional UML diagram showing inheritance hierarchy
- Showed all relationships: Agent → ReflexAgent, MultiAgentSearchAgent → {Minimax, AlphaBeta, Expectimax}
- AI helped me to understand the code.


Debugging Response:

**Provided the fix**:
```python
# BEFORE (incorrect):
alpha = max(alpha, maxValue)
if beta <= alpha:
    break

# AFTER (correct):
if value > alpha:
    alpha = value
if alpha > beta:
    break
```

## 5. What did you think of the response? Critique

Claude was an incredibly helpful learning assistant. The code support was clear and effective, and the debugging feedback was immediate and accurate. I made a deliberate effort to understand everything it provided, so I feel I achieved the learning objectives.

The alpha–beta pruning bug was the only technical issue, and it was identified and fixed within minutes. For a complex assignment involving multiple algorithms, this represents an impressive success rate.

When used responsibly, AI assistance like this can be a powerful learning tool. The key is ensuring you fully understand the material provided rather than copying it blindly.
