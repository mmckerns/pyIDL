import pyIDL

def test():
    '''test(); simple test of shape for IDL Arrays'''
    print "testing..."
    a = 1
    b = [1,2]
    c = [[1,2,3],[4,5,6]]
    s = 'foo'
    local = {'a':a, 'b':b, 'c':c, 's':s}
    print 'Input: %r' % local
    m = pyIDL.idl()
    m.put('a',a)
    m.put('b',b)
    m.put('c',c)
    m.put('s',s)
    print 'Local variables: %s' % m.who(local=True)
    print 'PRINTED Local variables: '
    m.who(local=True,stdout=True)
    print ''
    print 'IDL variables: %s' % m.who(local=False)
    print 'PRINTED IDL variables: '
    m.who(local=False,stdout=True)
    local['a'] = m.get('a')
    local['b'] = m.get('b')
    local['c'] = m.get('c')
    local['s'] = m.get('s')
    print 'Output: %r' % local
    return

if __name__ == '__main__':
    test()
