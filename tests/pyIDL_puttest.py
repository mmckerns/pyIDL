import pyIDL
import numarray

def test():
    '''test(); simple test of put for list and array'''
    A = 1
    B = [1,2]
    C = numarray.array(B)
    S = 'foo'
    T = numarray.array(S)

    vars = [A,B,C,S,T]
    m = pyIDL.idl()

    print "numarray imported..."
    print "testing put()...\n"
    x = raw_input("test ? > ")
    if x: exec "vars = ["+x+"]"

    for v in vars:

        vv = 'X'
        print "\nvalue = %r" % v
        print "RESULTS: whos[], get()"

        m.put(vv,v)
        print "no args: %r, %r" % (m.whos[vv],m.get(vv))

        m.put(vv,v,array=False)
        print "array=False: %r, %r" % (m.whos[vv],m.get(vv))
        m.put(vv,v,array='?')
        print "array=?: %r, %r" % (m.whos[vv],m.get(vv))
        m.put(vv,v,array=True)
        print "array=True: %r, %r" % (m.whos[vv],m.get(vv))
        m.put(vv,v,array='?')
        print "array=?: %r, %r" % (m.whos[vv],m.get(vv))

        m.put(vv,v,array=False,type='Int8')
        print "array=False,type=Int8: %r, %r" % (m.whos[vv],m.get(vv))
        m.put(vv,v,array='?',type='?')
        print "array=?,type=?: %r, %r" % (m.whos[vv],m.get(vv))
        m.put(vv,v,array='?',type='Int16')
        print "array=?,type=Int16: %r, %r" % (m.whos[vv],m.get(vv))
        m.put(vv,v,array=True,type='Int8')
        print "array=True,type=Int8: %r, %r" % (m.whos[vv],m.get(vv))
        m.put(vv,v,array='?',type='?')
        print "array=?,type=?: %r, %r" % (m.whos[vv],m.get(vv))
        try:
            m.put(vv,v,array='?',type='Int16')
            print "array=?,type=Int16: %r, %r" % (m.whos[vv],m.get(vv))
        except ValueError:
            print "array=?,type=Int16: raises ValueError..."
        m.delete(vv)

    return

if __name__ == '__main__':
    test()
