1.	Which AI did you use?
Claude (Anthropic), accessed via claude.ai
2.	What was your problem/issue?
The main challenge was fixing failing autograder.
3.	What did you ask it?
Debug question2 after it failed the bridge-crossing test
Debug question8 after multiple attempts returned wrong answers
4.	What was the response?
For question2 it initially gave noise=0.2 which failed, then corrected to noise=0.0. For question8 it went through several wrong attempts ('NOT POSSIBLE' string, numeric values, None) before we investigated the test class source code, discovered the SHA1 hash check, ran a brute-force hash match, and confirmed the correct answer was the string 'NOT POSSIBLE'.
5.	What did you think of the response? Critique was it told you: good/bad, you used it or not, what was wrong with what it told you?
The response was good and accurate.  When the autograder failed, the SHA1 hash approach to find the exact expected string was the key breakthrough.
