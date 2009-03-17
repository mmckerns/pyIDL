#Actually, searching recursively for invalid syntax is better, becuase it
# gives exit conditions...
#This code currently goes on an infinite loop.

import re

def check(expr):
    obj_bracket = re.compile('\[[^\[]+?\]')
    target = expr
    test = obj_bracket.search(target)
    while test:
        match = test.group()
        check(match[1:-1])
        target = target.replace('',match)
        test = obj_bracket.search(target)
        if not test: break
    print target
    if expr != target: check(target)

expr = raw_input('IDL> ')
check(str(expr))
print "OK"
