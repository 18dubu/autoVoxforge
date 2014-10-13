#import pycosat



def reduce_it(G):
    """ Input: an adjacency matrix G of arbitrary size represented as a list of lists.
        Output: the clauses of the cnf formula output in pycosat format.
        Each clause is be reprented as a list of nonzero integers.
        Positive numbers indicate positive literals, negatives negative literal.
        Thus, the clause (x_1 \vee \not x_5 \vee x_4) is represented
        as [1,-5,4].  A list of such lists is returned."""

    n = len(G)
    def X(i, j):
        """
        Returns the number of the variable corresponding to
        the ith vertex in the path being vertex j.
        """
        return n * (i-1) + j

    #the variable index

    myClauses = []
    #clauses
    #each node must appear in the path
    for j in range(1,n+1):
        currClause = []
        for k in range(1,n+1):
            currClause.append(X(k,j))
        myClauses.append(currClause)
    #no node appears twice in the path
    for j in range(1,n+1):
        for i in range(1,n):
            for k in range(i+1,n+1):
                myClauses.append([-1*int(X(i,j)), -1*int(X(k,j))])

    #every position in the path must be occupied
    for i in range(1,n+1):
        currClause = []
        for j in range(1,n+1):
            currClause.append(X(i,j))
        myClauses.append(currClause)
    #no two nodes in the same position
    for i in range(1,n+1):
        for j in range(1,n):
            for k in range(j+1,n+1):
                myClauses.append([-1*int(X(i,j)), -1*int(X(i,k))])
    #no-adjacenct nodes can be adjancent in the path
    for i in range(n):
        for j in range(n):
            if G[i][j] == 0:
                for k in range(1,n+1):
                    myClauses.append([-1*int(X(k,i+1)), -1*int(X(k+1,j+1))])

    return myClauses

def main():
    #A graph with a hamiltonian path
    G = [[0, 0, 0, 1, 1],
    [0, 0, 0, 0, 1],
    [0, 0, 0, 1, 0],
    [1, 0, 1, 0, 1],
    [1, 1, 0, 1, 0]]

    clauses = reduce_it(G)

    #sol = pycosat.solve(clauses)

    #assert(sol != 'UNSAT')

    #A graph without a hamiltonian path
    G = [[0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0]]

    clauses = reduce_it(G)

    #sol = pycosat.solve(clauses)

    #assert (sol == 'UNSAT')

if __name__ == "__main__":
    main()
    print 'done'