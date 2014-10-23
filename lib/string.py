#basic string opeartions
#author: Handong Ma

INF = 1.0e400

#input should be two lists
def stringMatching(stringList1, stringList2, replacementPenalty=1.5, gapPenalth = 1):
    #stringList1 = ['as', 'a','single','man','on', 'earth']
    #stringList2 = ['as','not', 'a','single','woman','on','the','earth']
    matchedString1 = []
    matchedString2 = []
    #string 1 as reference
    align = []  # align  list: Insertion, Deletion, Matching, Replacement
    #init DP matrix
    matrix = [[INF for x in range(len(stringList2)+1)] for y in range(len(stringList1)+1)]
    matrix[0] = [x for x in range(len(stringList2)+1)]
    for j in range(1, len(stringList1)+1):
        matrix[j][0] = j
    parent = {}
    for row in range(1,len(matrix)):
        for col in range(1,len(matrix[0])):
            if matrix[row-1][col] + gapPenalth < matrix[row][col]:  # go down to reach the target cell, INSERTION from string 1 (row) string 2 (col)
                matrix[row][col] = matrix[row-1][col] + gapPenalth
                parent[(row,col)] = (row-1,col)
                #align.append('D')
            if matrix[row][col-1] + gapPenalth < matrix[row][col]:  # go right to reach the target cell, DELETION from string 1 (row) string 2 (col)
                matrix[row][col] = matrix[row][col-1] + gapPenalth
                #align.append('I')
                parent[(row,col)] = (row,col-1)
            penalty = 0
            if not stringList1[row-1] == stringList2[col-1]:
                penalty = replacementPenalty
            if matrix[row-1][col-1] + penalty < matrix[row][col]:
                matrix[row][col] = matrix[row-1][col-1] + penalty
                parent[(row,col)] = (row-1,col-1)
    #trace back
    trace = []
    x = (len(matrix)-1,len(matrix[0])-1)
    while 1:
        pre_x = x
        trace.append(x)
        if pre_x[0] != 0 and pre_x[1] != 0:
            x = parent[pre_x]
        if pre_x[0] == 0 and pre_x[1] != 0:
            x = (pre_x[0], pre_x[1]-1)
        if pre_x[0] != 0 and pre_x[1] == 0:
            x = (pre_x[0]-1, pre_x[1])
        if pre_x[0]-x[0] != 0 and pre_x[1]-x[1] != 0:
            matchedString1.append(stringList1[pre_x[0]-1])
            matchedString2.append(stringList2[pre_x[1]-1])
            if stringList1[pre_x[0]-1] == stringList2[pre_x[1]-1]:
                align.append('M')
            else:
                align.append('R')
        if pre_x[0]-x[0] == 0 and pre_x[1]-x[1] != 0:  # go left right
            matchedString1.append('-')
            matchedString2.append(stringList2[pre_x[1]-1])
            align.append('I')
        if pre_x[0]-x[0] != 0 and pre_x[1]-x[1] == 0:  # go up down
            matchedString1.append(stringList1[pre_x[0]-1])
            matchedString2.append('-')
            align.append('D')
        if pre_x == (0, 0):
            break
    matchedString1.reverse()
    matchedString2.reverse()
    align.reverse()
    #print matchedString1, stringList1
    #print matchedString2, stringList2
    #print align
    return [matchedString1,matchedString2,align]

#stringMatching('this is a test case for function stringMatching'.split(),\
#               'that is not a valid test for function stringMatching'.split())
#output:
#['this', 'is', '-', 'a', '-', 'test', 'case', 'for', 'function', 'stringMatching']
#['that', 'is', 'not', 'a', 'valid', 'test', '-', 'for', 'function', 'stringMatching']
#['R', 'M', 'I', 'M', 'I', 'M', 'D', 'M', 'M', 'M']
