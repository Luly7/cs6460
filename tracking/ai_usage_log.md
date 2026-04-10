# AI Usage Log — Ghostbusters Project

**Project:** Ghostbusters  
**Maintained by:** Lourdes Castleton  
**Log started:** 2026-04-10  
---

### [2026-04-01] — Pacman Tracking Assignment (CS 6460)
- **Tool:** Claude (Anthropic), accessed via claude.ai
- **Problem/Issue:** The main challenge was fixing a failing autograder on the UC Berkeley Pacman tracking assignment.
- **What I Asked:** "Why is my normalize() function throwing a TypeError?"
- **Response:** Claude identified a typo in `normalize()` — `self[key/total]` was written instead of `self[key] / total`. It provided the corrected implementation and instructed me to re-run `python autograder.py -q q1` and `python autograder.py -q q2` from the tracking directory to verify the fix.
- **Critique:** Good. The response was accurate and directly resolved the issue. I used it — the fix worked and q1 and q2 passed after applying the correction. No issues with the advice given.
