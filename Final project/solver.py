import time
import sys
import random
nodesExpanded = 0


# Reads CNF file & sets up variables for the sudoku solver
def SetUpPuzzle(puzzle):
    clauses = []
    literal = 0
    with open(puzzle, "r") as puzzle:
        clauses.append([])
        numVariables = 0
        for row in puzzle:
            splitRow = row.split()
            if len(splitRow) != 0 and splitRow[0] not in ("p", "c"):
                for i in splitRow:
                    variable = int(i)
                    numVariables = max(numVariables, abs(variable))
                    if variable == 0:
                        clauses.append([])
                    else:
                        clauses[-1].append(variable)
            if splitRow[0] == "p":
                literal = int(splitRow[2])
        assert len(clauses[-1]) == 0
        clauses.pop()
        if (numVariables > literal):
            print("Puzzle is not in CNF")
            sys.exit(5)
    startTime = time.time()
    result = BacktrackingCore([], clauses)
    if result:
        print('Sudoku solved!')
    else:
        print('No solution found!')
    print('Time:', time.time() - startTime)
    print('Nodes expanded:', nodesExpanded)


# The core of the algorithm, backtracking
def BacktrackingCore(varlist, clauses):
    clauses, pureVars = PureLiteral(clauses)
    clauses, unitVars = UnitPropagation(clauses)
    if clauses != -1:
        clauses, failedVars = FailedLiteral(clauses)
        varlist += (unitVars + pureVars + failedVars)
    else:
        varlist = (unitVars + pureVars + failedVars)
    if clauses == -1:
        return []
    if not clauses:
        return varlist
    V = random.choice(list(NumOccurences(clauses)))
    ret = BacktrackingCore(varlist+[V], EliminateClause(clauses, V))
    if not ret:
        ret = BacktrackingCore(varlist+[-V], EliminateClause(clauses, -V))
    return ret


# Inference technique I: Unit Propagation
def UnitPropagation(clauses):
    unitList = []
    unitClauses = [clause for clause in clauses if len(clause) == 1] 
    while len(unitClauses) >= 1: 
        unit = unitClauses[0]
        clauses = EliminateClause(clauses, unit[0]) 
        unitList += [unit[0]]
        if clauses == -1:
            return -1, []
        if not clauses:
            return clauses, unitList
        unitClauses = [clause for clause in clauses if len(clause) == 1] # Potential optimization
    return clauses, unitList


# Inference technique II: Failed Literal
def FailedLiteral(clauses):
    occ = {lit for clause in clauses for lit in clause}
    unitList = []
    for v in occ:
        clauses.append([v])
        tempClauses, unitList = UnitPropagation(clauses)
        if tempClauses == -1:
            del clauses[-1]
            clauses.append([-v])
            clauses, _ = UnitPropagation(clauses)
            if clauses == -1:
                return -1, []
            unitList.append(-v)
            continue
        else:
            del clauses[-1]
        clauses.append([-v])
        tempClauses, unitList = UnitPropagation(clauses)
        if tempClauses == -1:
            del clauses[-1]
            clauses.append([v])
            clauses, _ = UnitPropagation(clauses)
            if clauses == -1:
                return -1, []
            unitList.append(v)
        else:
            del clauses[-1]

    return clauses, unitList


# Inference technique III: Pure Literals
def PureLiteral(clauses):
    if clauses == -1:
        return -1, []
    pureList = []
    pureLiterals = []
    occ = NumOccurences(clauses)
    for i, j in occ.items():
        if -i not in occ: 
            pureLiterals.append(i) 
    for pure in pureLiterals:
        clauses = EliminateClause(clauses, pure) 
    pureList += pureLiterals
    return clauses, pureList


# Helper function I: helps remove clauses based on assignment
def EliminateClause(clauses, V):
    global nodesExpanded
    newclauses = []
    for clause in clauses:
        if V in clause:
            continue 
        if -V in clause:
            unit = []
            for literal in clause:
                if literal != -V:
                    unit.append(literal)
            if len(unit) == 0:
                return -1
            newclauses.append(unit)
        else:
            newclauses.append(clause)
    nodesExpanded += 1
    return newclauses


# Helper function II: gets number of occurences for each variable and stores in a dict
def NumOccurences(clauses): 
    occurences = {}
    for clause in clauses:
        for literal in clause:
            if literal in occurences:
                occurences[literal] += 1
            else:
                occurences[literal] = 1
    return occurences


# Code entry point: converts sudoku board to CNF
# Taken & modified from https://users.aalto.fi/~tjunttil/2020-DP-AUT/notes-sat/solving.html
if __name__ == '__main__':
    D = 3
    N = D*D
    file_name = sys.argv[1]
    clues = []
    digits = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9}
    with open(file_name, "r") as f:
        for line in f.readlines():
            assert len(line.strip()) == N, "'"+line+"'"
            for c in range(0, N):
                assert(line[c] in digits.keys() or line[c] == '.')
            clues.append(line.strip())
    assert(len(clues) == N)
    def var(r, c, v):
        assert(1 <= r and r <= N and 1 <= c and c <= N and 1 <= v and v <= N)
        return (r-1)*N*N+(c-1)*N+(v-1)+1
    cls = []
    for r in range(1,N+1):
        for c in range(1, N+1):
            cls.append([var(r,c,v) for v in range(1,N+1)])
            for v in range(1, N+1):
                for w in range(v+1,N+1):
                    cls.append([-var(r,c,v), -var(r,c,w)])
    for v in range(1, N+1):
        for r in range(1, N+1): cls.append([var(r,c,v) for c in range(1,N+1)])
        for c in range(1, N+1): cls.append([var(r,c,v) for r in range(1,N+1)])
        for sr in range(0,D):
            for sc in range(0,D):
                cls.append([var(sr*D+rd,sc*D+cd,v)
                            for rd in range(1,D+1) for cd in range(1,D+1)])
    for r in range(1, N+1):
        for c in range(1, N+1):
            if clues[r-1][c-1] in digits.keys():
                cls.append([var(r,c,digits[clues[r-1][c-1]])])
    output_filename = "cnf_output.cnf"
    f = open(output_filename, "w")
    f.write("p cnf " + str(max(map(max, cls))) + " " + str(len(cls)) + "\n")
    for c in cls:
        f.write(" ".join([str(l) for l in c])+" 0\n")
    f.close()
    SetUpPuzzle(output_filename)
