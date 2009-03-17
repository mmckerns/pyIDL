#!/usr/bin/env python
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  pyIDLtest.py
#  
#  4/11/2005 version 0.0.1a
#  mmckerns@caltech.edu
#  (C) 2005 All Rights Reserved
# 
#  <LicenseText>
# 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
from pyIDL import idl as IDL
from numarray import *
from numarray import strings as numstring

import unittest

#FIXME: stuff here _works_, but can crash with Segfault
#       or produce wrong results... due to buffer speed?

class PyIDL_rsiIDL_TestCase(unittest.TestCase):
    def setUp(self):
        '''IDL: instantiate a pyIDL session'''
        self.session = IDL(stdout=False)
        self.int = 1
        self.list = [1,2]
        self.array = array(self.list)
        self.dict = {}
        self.matrix = [[1,2,3],[4,5,6]] #XXX: add this to ALL/MOST tests!
        self.none = None
        self.str = 'foo'
        self.bytearray = array(self.str)
        self.strlist = ["hello", "world"]
        self.chararray = numstring.array(self.strlist)
        return #FIXME: do I want a new session for each test?

    def tearDown(self):
        '''IDL: destroy a pyIDL session'''
        self.session.pyidl.eval('.full_reset_session')
        self.session = None
        return #FIXME: do I want a new session for each test?

    def test_IDLput2b(self):
        '''IDL: put a variable into IDL (part IIb)'''
        self.assert_(self.session.put("b",self.list,array=False) == None,
                     "failure to pass a list to IDL")
        self.assert_(self.session.put("b",self.list,array='?') == None,
                     "failure to pass a list to IDL")
        b = self.session.pyidl.getvar('B')
        self.assertEqual(self.list,self.session._processobj(b))
        return

    def test_IDLput2(self):
        '''IDL: put a variable into IDL (part II)'''
        #check array
        self.assert_(self.session.put("b",self.list,array=True) == None,
                     "failure to pass a list to IDL as array")
        self.assert_(self.session.put("b",self.list,array='?') == None,
                     "failure to pass a list to IDL as array")
        b = self.session.pyidl.getvar('B')
        bb = self.session._processobj(b)
        self.assertEqual(all(self.array),all(bb))
        self.assertEqual(self.session._checkarray('',array(self.list)),\
                         self.session._checkarray('',bb))
#       self.assert_(self.session.put("b",self.list,array=False) == None,
#                    "failure to pass a list to IDL")
#       self.assert_(self.session.put("b",self.list,array='?') == None,
#                    "failure to pass a list to IDL")
#       b = self.session.pyidl.getvar('B')
#       self.assertEqual(self.list,self.session._processobj(b))
        self.assert_(self.session.put("s",self.str,array=True) == None,
                     "failure to pass a str to IDL as bytearray")
        self.assert_(self.session.put("s",self.str,array='?') == None,
                     "failure to pass a str to IDL as bytearray")
        s = self.session.pyidl.getvar('S')
        ss = self.session._processobj(s)
        self.assertEqual(all(self.array),all(ss))
        self.assertEqual(self.session._checkarray('',array(self.str)),\
                         self.session._checkarray('',ss))
        self.assert_(self.session.put("s",self.str,array=False) == None,
                     "failure to pass a str to IDL")
        self.assert_(self.session.put("s",self.str,array='?') == None,
                     "failure to pass a str to IDL")
        self.assertEqual(self.str,self.session.pyidl.getvar('S'))
        #specify type
        self.assert_(self.session.put("a",self.int,type='Int16') == None,
                     "failure to pass an int that ignores type to IDL")
        self.assertEqual(self.int, self.session.get('a'))
        self.assertEqual(self.int, self.session._getlocal('a'))
        self.assertEqual(self.int, self.session.who('a'))
        self.assertEqual(self.int, self.session.who('a',local=True))
        self.session.delete('A')
        self.assert_(self.session.put("b",self.list,type='Int16') == None,
                     "failure to pass a list that ignores type to IDL")
        self.assertEqual(self.list, self.session.get('b'))
        self.assertEqual(self.list, self.session._getlocal('b'))
        self.assertEqual(self.list, self.session.who('b'))
        self.assertEqual(self.list, self.session.who('b',local=True))
        self.session.delete('B')
        self.assert_(self.session.put("c",self.array,type='Int16') == None,
                     "failure to pass an array of specified type to IDL")
        Z = array(self.array,type='Int16')
        self.assertEqual(all(Z), all(self.session.get('c')))
        self.assertEqual(all(Z), all(self.session._getlocal('c')))
        self.assertEqual(all(Z), all(self.session.who('c')))
        self.assertEqual(all(Z), all(self.session.who('c',local=True)))
        self.assertEqual(self.session._checkarray('',self.array,type='Int16'),\
                         self.session._checkarray('',self.session.get('c')))
        self.session.delete('C')
        self.assert_(self.session.put("u",self.strlist,type='Int16') == None,
                     "failure to pass an strlist that ignores type to IDL")
        self.assertEqual(self.strlist, self.session.get('u'))
        self.assertEqual(self.strlist, self.session._getlocal('u'))
        self.assertEqual(self.strlist, self.session.who('u'))
        self.assertEqual(self.strlist, self.session.who('u',local=True))
        self.session.delete('U')
        #check type
        self.assert_(self.session.put("c",self.array,type='Int16') == None,
                     "failure to pass an array of specified type to IDL")
        self.assert_(self.session.put("c",self.array,type='?') == None,
                     "failure to pass an array with type lookup to IDL")
        Z = array(self.array,type='Int16')
        self.assertEqual(all(Z), all(self.session.get('c')))
        self.assertEqual(all(Z), all(self.session._getlocal('c')))
        self.assertEqual(all(Z), all(self.session.who('c')))
        self.assertEqual(all(Z), all(self.session.who('c',local=True)))
        self.session.delete('C')
        return

if __name__ == "__main__":
    suite0 = unittest.makeSuite(PyIDL_rsiIDL_TestCase)
    alltests = unittest.TestSuite((suite0,))
    unittest.TextTestRunner(verbosity=2).run(alltests)


#  End of file 
