import pyIDL

def test():
    '''test(); simple test of who for variable and array'''
    print "testing..."
    x = 69
    y = [[2,4],[7,8]]
    z = 'foobar'
    a = [1,2,3]
    input = [x,y,z,a]
    print 'Input: %s' % input
    m = pyIDL.idl()
    m.put('x',x)
    m.put('y',y)
    m.put('z',z)
    m.put('a',a,array=True,type='Float64')
    print 'Local variables: %s' % m.who(local=True)
    print 'PRINTED Local variables: '
    m.who(local=True,stdout=True)
    print 'IDL variables: %s' % m.who(local=False)
    print 'PRINTED IDL variables: '
    m.who(local=False,stdout=True)
    x = m.get('x')
    y = m.get('y')
    z = m.get('z')
    a = m.get('a',array=True)
    output = [x,y,z,a]
    print 'Output: %s' % output
    return

if __name__ == '__main__':
    test()
