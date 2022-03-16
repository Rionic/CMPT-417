board_list contains test instances. Paste this into board.txt, and then run python solver.py board.txt to run the solver on the given instance.
The board will be converted into cnf in the file cnf_output.cnf in main, then read by the SetUpPuzzle function. After this, the algorithm will run.

The current code runs all three inference techniques.

To run any combination of Pure Elimination / Unit Propagation / Failed Literal, comment them in at lines 43 / 44 / 46 respectively, 
and add their second return values, (unitVars, failedVars, pureVars), to the varlist on lines 49 and 47 (where varlist is assigned). 
Make sure to encapsulate assignees in parenthesis ().

The command line will output the running time, nodes expanded, and whether the instance was solved.