import pyIDL
m = pyIDL.idl()

def test():
    '''test(); simple test of reading pros'''
    print "testing..."
    print "Output using 'eval' should be 'False, True, True, False'"
    m.eval("foo")
    m.eval("foo,/arg")
    m.eval("foo,arg=1")
    m.eval("foo,arg=0")
    return

def test2(): 
    '''test2(); simple test of boolean logic'''
    print "testing..."
    print "Output without 'eval' should be 'False, False, True, True, False'"
    m.foo()
    m.foo(arg=False)
    m.foo(arg=True)
    m.foo(arg=1)
    m.foo(arg=0)
    return

if __name__ == '__main__':
    test()
    test2()
