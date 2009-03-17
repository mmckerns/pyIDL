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

#   def test_IDLdependancy(self):
#       '''IDL: check package dependancies'''
#       self.assert_(exec 'import numarray' == None,
#                    "failure to import numarray")
#       return

    def test_IDL_validate(self):
        '''IDL: fail upon invalid name'''
        self.assert_(self.session._validate("foo") == None,
                     "failure to validate a valid variable")
        self.assert_(self.session._validate("f_o$1o") == None,
                     "failure to validate a valid variable")
        self.assertRaises(NameError,self.session._validate,'1foo')
        self.assertRaises(NameError,self.session._validate,'$foo')
        self.assertRaises(NameError,self.session._validate,'f.oo')
        self.assertRaises(NameError,self.session._validate,'foo!')
        self.assertRaises(NameError,self.session._validate,'for')
        return

    def test_IDL_validatestore(self):
        '''IDL: fail if invalid store'''
        Z = self.session.whos
        self.assert_(self.session._validatestore("whos") == None,
                     "failure to validate a valid store string")
        self.assertRaises(NameError,self.session._validatestore,self.int)
        self.assertRaises(NameError,self.session._validatestore,self.list)
        self.assertRaises(NameError,self.session._validatestore,self.array)
        self.assertRaises(NameError,self.session._validatestore,self.dict)
        self.assertRaises(NameError,self.session._validatestore,self.none)
        self.assertRaises(NameError,self.session._validatestore,self.str)
        self.assertRaises(NameError,self.session._validatestore,self.bytearray)
        self.assertRaises(NameError,self.session._validatestore,self.strlist)
        self.assertRaises(NameError,self.session._validatestore,self.chararray)
        self.assertRaises(NameError,self.session._validatestore,'X')
        self.assertRaises(NameError,self.session._validatestore,Z)
        return

    def test_IDL_putlocal(self):
        '''IDL: add variable to local store'''
        Z = 666
        self.assert_(self.session._putlocal("a",self.int) == None,
                     "failure to add scalar to local store")
        self.assert_(self.session._putlocal("b",self.list) == None,
                     "failure to add list to local store")
        self.assert_(self.session._putlocal("c",self.array) == None,
                     "failure to add array to local store")
        self.assert_(self.session._putlocal("n",self.none) == None,
                     "failure to add None to local store")
        self.assert_(self.session._putlocal("s",self.str) == None,
                     "failure to add string to local store")
        self.assert_(self.session._putlocal("z",Z,store='whos') == None,
                     "failure to add to named local store")
        self.assertEqual(self.int, self.session.whos['A'])
        self.assertEqual(self.list, self.session.whos['B'])
        self.assertEqual(all(self.array), all(self.session.whos['C']))
        self.assertEqual(self.none, self.session.whos['N'])
        self.assertEqual(self.str, self.session.whos['S'])
        self.assertEqual(Z, self.session.whos['Z'])
        self.assertRaises(NameError,self.session._putlocal,'foo!',69)
        return

    def test_IDL_getlocal(self):
        '''IDL: return variable value from local store'''
        Z = 666
        self.session.whos['A'] = self.int
        self.session.whos['B'] = self.list
        self.session.whos['C'] = self.array
        self.session.whos['N'] = self.none
        self.session.whos['S'] = self.str
        self.session.whos['Z'] = Z
        self.assertEqual(self.int, self.session._getlocal('a'))
        self.assertEqual(self.list, self.session._getlocal('b'))
        self.assertEqual(all(self.array), all(self.session._getlocal('c')))
        self.assertEqual(self.none, self.session._getlocal('n'))
        self.assertEqual(self.str, self.session._getlocal('s'))
        self.assertEqual(Z, self.session._getlocal('z',store='whos'))
        self.assertEqual(None, self.session._getlocal('x')) #KeyError not raised
        self.assertEqual(self.int, self.session._getlocal('a',skip=False))
        self.assertRaises(NameError, self.session._getlocal,'x',skip=False)
        return

    def test_IDL_poplocal(self):
        '''IDL: delete variable from local store'''
        Z = 666
        self.session.whos['A'] = self.int
        self.session.whos['B'] = self.list
        self.session.whos['C'] = self.array
        self.session.whos['N'] = self.none
        self.session.whos['S'] = self.str
        self.session.whos['Z'] = Z
        self.assertEqual(self.int, self.session._poplocal('a'))
        self.assertEqual(self.list, self.session._poplocal('b'))
        self.assertEqual(all(self.array), all(self.session._poplocal('c')))
        self.assertEqual(self.none, self.session._poplocal('n'))
        self.assertEqual(self.str, self.session._poplocal('s'))
        self.assertEqual(Z, self.session._poplocal('z',store='whos'))
        self.assertEqual(None, self.session._poplocal('x')) #KeyError not raised
        self.assertEqual({},self.session.whos)
        return

    def test_IDL_islist(self):
        '''IDL: check if local variable is list'''
        self.session._putlocal("a",self.int)
        self.session._putlocal("b",self.list)
        self.session._putlocal("c",self.array)
        self.session._putlocal("n",self.none)
        self.session._putlocal("s",self.str)
        self.session._putlocal("t",self.bytearray)
        self.session._putlocal("u",self.strlist)
        self.session._putlocal("v",self.chararray)
        self.assertEqual(False, self.session._islist('a'))
        self.assertEqual(True, self.session._islist('b'))
        self.assertEqual(False, self.session._islist('c'))
        self.assertEqual(False, self.session._islist('n'))
        self.assertEqual(False, self.session._islist('s'))
        self.assertEqual(False, self.session._islist('t'))
        self.assertEqual(True, self.session._islist('u'))
        self.assertEqual(False, self.session._islist('v'))
        self.assertEqual(False, self.session._islist('x'))
        return

    def test_IDL_isarray(self):
        '''IDL: check if local variable is array'''
        self.session._putlocal("a",self.int)
        self.session._putlocal("b",self.list)
        self.session._putlocal("c",self.array)
        self.session._putlocal("n",self.none)
        self.session._putlocal("s",self.str)
        self.session._putlocal("t",self.bytearray)
        self.session._putlocal("u",self.strlist)
        self.session._putlocal("v",self.chararray)
        self.assertEqual(False, self.session._isarray('a'))
        self.assertEqual(False, self.session._isarray('b'))
        self.assertEqual(True, self.session._isarray('c'))
        self.assertEqual(False, self.session._isarray('n'))
        self.assertEqual(False, self.session._isarray('s'))
        self.assertEqual(True, self.session._isarray('t'))
        self.assertEqual(False, self.session._isarray('u'))
        self.assertEqual(False, self.session._isarray('v'))
        self.assertEqual(False, self.session._isarray('x'))
        return

    def test_IDL_ischararray(self):
        '''IDL: check if local variable is CharArray'''
        self.session._putlocal("a",self.int)
        self.session._putlocal("b",self.list)
        self.session._putlocal("c",self.array)
        self.session._putlocal("n",self.none)
        self.session._putlocal("s",self.str)
        self.session._putlocal("t",self.bytearray)
        self.session._putlocal("u",self.strlist)
        self.session._putlocal("v",self.chararray)
        self.assertEqual(False, self.session._ischararray('a'))
        self.assertEqual(False, self.session._ischararray('b'))
        self.assertEqual(False, self.session._ischararray('c'))
        self.assertEqual(False, self.session._ischararray('n'))
        self.assertEqual(False, self.session._ischararray('s'))
        self.assertEqual(False, self.session._ischararray('t'))
        self.assertEqual(False, self.session._ischararray('u'))
        self.assertEqual(True, self.session._ischararray('v'))
        self.assertEqual(False, self.session._ischararray('x'))
        return

    def test_IDL_toarray(self):
        '''IDL: check against the default if convert to array'''
        self.session._putlocal("a",self.int)
        self.session._putlocal("b",self.list)
        self.session._putlocal("c",self.array)
        self.assertEqual(False,self.session._toarray('a',default='list'))
        self.assertEqual(False,self.session._toarray('b',default='list'))
        self.assertEqual(True,self.session._toarray('c',default='list'))
        self.assertEqual(True,self.session._toarray('a',default='array'))
        self.assertEqual(False,self.session._toarray('b',default='array'))
        self.assertEqual(True,self.session._toarray('c',default='array'))
        return

    def test_IDL_totype(self):
        '''IDL: check array type'''
        self.session._putlocal("a",self.int)
        self.session._putlocal("b",self.list)
        self.session._putlocal("c",self.array)
        self.session._putlocal("d",self.dict)
        self.session._putlocal("s",self.str)
        self.session._putlocal("t",self.bytearray)
        self.assertEqual(None,self.session._totype('a'))
        self.assertEqual(None,self.session._totype('b'))
       #self.assertEqual('Int32',self.session._totype('c')) #Int64 on a64
        self.assertEqual(None,self.session._totype('d'))
        self.assertEqual(None,self.session._totype('s'))
        self.assertEqual('Int8',self.session._totype('t'))
        return

    def test_IDL_wholist(self):
        '''IDL: check list of string names for all IDL variables'''
        self.session.pyidl.eval("a = 1")
        self.session.pyidl.eval("b = [1,2]")
        self.session.pyidl.eval("s = 'foo'")
        self.session._putvar("n",None,allowNone=True)
        wholist = ['A', 'B', 'N', 'S']
        self.assertEqual(wholist, self.session._wholist())
        return

    def test_IDL_exists(self):
        '''IDL: check if IDL variable exists'''
        self.session.pyidl.eval("a = 1")
        self.assertEqual(True, self.session._exists('a'))
        self.assertEqual(False, self.session._exists('b'))
        return

    def test_IDL_isarrayobj(self):
        '''IDL: check if is IDL_array obj'''
        self.session.pyidl.eval("a = 1")
        self.session.pyidl.eval("b = [1,2]")
        self.session.pyidl.eval("s = 'foo'")
        self.session.pyidl.eval("t = BYTE(s)")
        self.session.pyidl.eval("u = STRING(b)")
        a = self.session.pyidl.getvar('A')
        b = self.session.pyidl.getvar('B')
        s = self.session.pyidl.getvar('S')
        t = self.session.pyidl.getvar('T')
        u = self.session.pyidl.getvar('U')
        self.assertEqual(False, self.session._isarrayobj(a))
        self.assertEqual(True, self.session._isarrayobj(b))
        self.assertEqual(False, self.session._isarrayobj(s))
        self.assertEqual(True, self.session._isarrayobj(t))
        self.assertEqual(True, self.session._isarrayobj(u))
        self.assertEqual(False, self.session._isarrayobj(self.int))
        self.assertEqual(False, self.session._isarrayobj(self.list))
        self.assertEqual(False, self.session._isarrayobj(self.array))
        self.assertEqual(False, self.session._isarrayobj(self.none))
        self.assertEqual(False, self.session._isarrayobj(self.str))
        self.assertEqual(False, self.session._isarrayobj(self.bytearray))
        self.assertEqual(False, self.session._isarrayobj(self.chararray))
        return

    def test_IDL_invertshape(self):
        '''IDL: translate shape between IDL and NumArray'''
        self.assertEqual((),self.session._invertshape(()))
        self.assertEqual((1,),self.session._invertshape((1,)))
        self.assertEqual((3,2),self.session._invertshape((2,3)))
        self.assertEqual((2,3,4,5),self.session._invertshape((5,4,3,2)))
        self.assertRaises(TypeError,self.session._invertshape,self.int)
        self.assertRaises(TypeError,self.session._invertshape,self.list)
        self.assertRaises(TypeError,self.session._invertshape,self.dict)
        self.assertRaises(TypeError,self.session._invertshape,self.none)
        return


    def test_IDL_putstringarr(self):
        '''IDL: push list of strings as IDL STRING Array'''
        self.assert_(self.session._putstringarr("v",self.strlist) == None,
                     "failure to pass a list of strings to IDL as a STRING")
        v = self.session.pyidl.getvar('V')
        tmp = 'azsxdcfvgb'
        sep = '10b' #XXX: 10b = Unix, 13b = Mac, 10b13b = Windows?
        self.session.pyidl.eval(tmp+" = '"+tmp+"'")
        self.session.pyidl.eval(tmp+" = STRJOIN("+v.name()+", STRING("+sep+"))")
        val = self.session.pyidl.getvar(tmp).split()
        self.assertEqual(self.strlist,val)
        self.assert_(self.session._putstringarr("b",self.list) == None,
                     "failure to pass a list to IDL as a STRING")
        b = self.session.pyidl.getvar('B')
        tmp = 'azsxdcfvgb'
        sep = '10b' #XXX: 10b = Unix, 13b = Mac, 10b13b = Windows?
        self.session.pyidl.eval(tmp+" = '"+tmp+"'")
        self.session.pyidl.eval(tmp+" = STRJOIN("+b.name()+", STRING("+sep+"))")
        val = self.session.pyidl.getvar(tmp).split()
        Z = self.list
        for i in range(len(Z)): Z[i] = str(Z[i])
        self.assertEqual(Z,val)
        self.assertRaises(TypeError,self.session._putstringarr,self.int)
        self.assertRaises(TypeError,self.session._putstringarr,self.array)
        self.assertRaises(TypeError,self.session._putstringarr,self.dict)
        self.assertRaises(TypeError,self.session._putstringarr,self.none)
        self.assertRaises(TypeError,self.session._putstringarr,self.str)
        self.assertRaises(TypeError,self.session._putstringarr,self.bytearray)
        self.assertRaises(TypeError,self.session._putstringarr,self.chararray)
        return

    def test_IDL_processstringarrayobj(self):
        '''IDL: convert IDL STRING Array to list of strings'''
        self.session.pyidl.eval("a = 1")
        self.session.pyidl.eval("b = [1,2]")
        self.session.pyidl.eval("s = 'foo'")
        self.session.pyidl.eval("t = BYTE(s)")
        self.session.pyidl.eval("u = STRING(b)")
        Z = ['1', '2']
        u = self.session.pyidl.getvar('U')
        self.assertEqual(Z,self.session._processstringarrayobj(u))
        u = self.session.pyidl.getvar('U') #repeat test should succeed
        self.assertEqual(Z,self.session._processstringarrayobj(u))
        u = self.session.pyidl.getvar('U') #repeat test should succeed x2
        self.assertEqual(Z,self.session._processstringarrayobj(u))
        #failures
        a = self.session.pyidl.getvar('A')
        b = self.session.pyidl.getvar('B')
        s = self.session.pyidl.getvar('S')
        t = self.session.pyidl.getvar('T')
        self.assertRaises(TypeError,self.session._processstringarrayobj,a)
        self.assertRaises(TypeError,self.session._processstringarrayobj,b)
        self.assertRaises(TypeError,self.session._processstringarrayobj,s)
        self.assertRaises(TypeError,self.session._processstringarrayobj,t)
        self.assertRaises(TypeError,\
                          self.session._processstringarrayobj,self.int)
        self.assertRaises(TypeError,\
                          self.session._processstringarrayobj,self.list)
        self.assertRaises(TypeError,\
                          self.session._processstringarrayobj,self.array)
        self.assertRaises(TypeError,\
                          self.session._processstringarrayobj,self.none)
        self.assertRaises(TypeError,\
                          self.session._processstringarrayobj,self.str)
        return

    def test_IDL_processobj(self):
        '''IDL: convert IDL_array obj to value'''
        self.session.pyidl.eval("a = 1")
        self.session.pyidl.eval("b = [1,2]")
        self.session.pyidl.eval("r = [1]")
        self.session.pyidl.eval("s = 'foo'")
        self.session.pyidl.eval("t = BYTE(s)")
        self.session.pyidl.eval("u = STRING(b)")
        b = self.session.pyidl.getvar('B')
        self.assertEqual(self.list,self.session._processobj(b,False))
        b = self.session.pyidl.getvar('B') #repeat test should succeed
        self.assertEqual(self.list,self.session._processobj(b,False))
        b = self.session.pyidl.getvar('B') #repeat test should succeed X2 
        self.assertEqual(self.list,self.session._processobj(b,False))
        b = self.session.pyidl.getvar('B')
        self.assertEqual(all(self.array),all(self.session._processobj(b,True)))
        self.assertEqual(b,self.session.getbuff['B'])
        #BYTE Array
        t = self.session.pyidl.getvar('T')
        self.assertEqual(self.str,self.session._processobj(t,False))
        t = self.session.pyidl.getvar('T')
        self.assertEqual(all(self.bytearray),\
                         all(self.session._processobj(t,True)))
        #STRING Array
        Z = ['1', '2']
        u = self.session.pyidl.getvar('U')
        self.assertEqual(Z, self.session._processobj(u,False))
        u = self.session.pyidl.getvar('U')
        self.assertEqual(Z, self.session._processobj(u,True))
        #rank-0 Arrays  #XXX: also needs put('a',1,array=True)???
        r = self.session.pyidl.getvar('R')
        self.assertEqual([self.int],self.session._processobj(r,False))
        r = self.session.pyidl.getvar('R')
        self.assertEqual(all(array(self.int)),\
                         all(self.session._processobj(r,True)))
        #failures
        a = self.session.pyidl.getvar('A')
        s = self.session.pyidl.getvar('S')
        self.assertRaises(TypeError,self.session._processobj,a)
        self.assertRaises(TypeError,self.session._processobj,s)
        self.assertRaises(TypeError,self.session._processobj,self.int)
        self.assertRaises(TypeError,self.session._processobj,self.list)
        self.assertRaises(TypeError,self.session._processobj,self.array)
        self.assertRaises(TypeError,self.session._processobj,self.none)
        self.assertRaises(TypeError,self.session._processobj,self.str)
        return

    def test_IDL_putvar(self):
        '''IDL: put a scalar into IDL'''
        self.assert_(self.session._putvar("a",self.int) == None,
                     "failure to pass an int to IDL")
        self.assert_(self.session._putvar("s",self.str) == None,
                     "failure to pass a string to IDL")
        self.assertEqual(self.int, self.session.get('a'))
        self.assertEqual(self.int, self.session._getlocal('a'))
        self.assertEqual(self.str, self.session.get('s'))
        self.assertEqual(self.str, self.session._getlocal('s'))
        self.assertRaises(TypeError,self.session._putvar,'b',self.list)
        self.assertRaises(TypeError,self.session._putvar,'c',self.array)
        self.assertRaises(TypeError,self.session._putvar,'d',self.dict)
        self.assertRaises(ValueError,self.session._putvar,'n',self.none)
        self.assertRaises(TypeError,self.session._putvar,'t',self.bytearray)
        self.assertRaises(TypeError,self.session._putvar,'u',self.strlist)
        self.assertRaises(TypeError,self.session._putvar,'v',self.chararray)
        whos = {'A':self.int, 'S':self.str}
        self.assertEqual(whos, self.session.who())
        self.assertEqual(whos, self.session.who(local=True))
        #bad with exists
        self.assertRaises(TypeError,self.session._putvar,'A',{})
        self.assertEqual(whos, self.session.who())
        self.assertEqual(whos, self.session.who(local=True))
        #None with exists
        self.assertRaises(ValueError,self.session._putvar,'S',None)
        self.assertEqual(whos, self.session.who())
        self.assertEqual(whos, self.session.who(local=True))
        #None with allowNone
        self.assert_(self.session._putvar("n",self.none,allowNone=True) == None,
                     "failure to pass a None to IDL")
        whos['N'] = self.none
        self.assertEqual(whos, self.session.who())
        self.assertEqual(whos, self.session.who(local=True))
        #None with exists and allowNone
        self.assert_(self.session._putvar("s",None,allowNone=True) == None,
                     "failure to pass a None to IDL")
        whos['S'] = None
        self.assertEqual(whos, self.session.who())
        self.assertEqual(whos, self.session.who(local=True))
        return

    def test_IDL_checkarray(self):
        '''IDL: check array and type'''
        self.assertEqual((False,None),self.session._checkarray('a',self.int))
        self.assertEqual((False,None),self.session._checkarray('b',self.list))
        self.assertEqual((True,self.array.type()),\
             self.session._checkarray('c',self.array))
        #array=False
        self.assertEqual((False,None),\
             self.session._checkarray('a',self.int,array=False))
        self.assertEqual((False,None),\
             self.session._checkarray('b',self.list,array=False))
        self.assertEqual((False,None),\
             self.session._checkarray('c',self.array,array=False))
        #array=False, type
        self.assertEqual((False,None),\
             self.session._checkarray('a',self.int,array=False,type='Int16'))
        self.assertEqual((False,None),\
             self.session._checkarray('b',self.list,array=False,type='Int16'))
        self.assertEqual((False,None),\
             self.session._checkarray('c',self.array,array=False,type='Int16'))
        #array=True
        self.assertEqual((True,None),\
             self.session._checkarray('a',self.int,array=True))
        self.assertEqual((True,None),\
             self.session._checkarray('b',self.list,array=True))
        self.assertEqual((True,self.array.type()),\
             self.session._checkarray('c',self.array,array=True))
        #array=True, type
        self.assertEqual((True,'Int16'),\
             self.session._checkarray('a',self.int,array=True,type='Int16'))
        self.assertEqual((True,'Int16'),\
             self.session._checkarray('b',self.list,array=True,type='Int16'))
        self.assertEqual((True,'Int16'),\
             self.session._checkarray('c',self.array,array=True,type='Int16'))
        #XXX: tests for '?' same as _toarray & _totype
        self.assertEqual((False,None),\
             self.session._checkarray('a',self.int,array='?',type='?'))
        return

    def test_IDL_delarr(self):
        '''IDL: delete array from all local stores and IDL'''
        self.session._putvar('a',self.int)
        self.session.put('b',self.list)
        self.session.put('c',self.array,array=True)
        self.session._putvar('n',self.none,allowNone=True)
        self.session._putvar('s',self.str)
        self.session.put('t',self.bytearray,array=True)
        self.session._putstringarr('u',self.strlist)
        self.assert_(self.session._delarr("a") == None,
                     "failure to pass on delete of int")
        self.assert_(self.session._delarr("b") == None,
                     "failure to delete list")
        self.assert_(self.session._delarr("c") == None,
                     "failure to delete array")
        self.assert_(self.session._delarr("n") == None,
                     "failure to pass on delete of None")
        self.assert_(self.session._delarr("s") == None,
                     "failure to pass on delete of string")
        self.assert_(self.session._delarr("t") == None,
                     "failure to delete bytearray")
        self.assert_(self.session._delarr("u") == None,
                     "failure to pass on delete of strlist")
        self.assert_(self.session._delarr("x") == None,
                     "failure to pass on delete of undefined")
        whos = {'A':self.int, 'S':self.str, 'N':self.none, 'U':self.strlist}
        self.assertEqual(whos,self.session.whos)
        self.assertEqual({},self.session.getbuff)
        self.assertEqual({},self.session.putbuff)
        return

    def test_IDL_synclocal(self):
        '''IDL: update local store value to IDL value'''
        Q = 'bar'
        W = [6,9]
        X = 666
        Y = 'baz'
        Z = 69
        self.session._putvar('z',Z)
        self.session.put('c',self.array)
        self.session._putvar('n',self.none,allowNone=True)
        self.session._putvar('q',Q)
        self.session.pyidl.eval("a = 1")
        self.session.pyidl.eval("b = [1,2]")
        self.session.pyidl.eval("s = 'foo'")
        self.session._putlocal('w',W)
        self.session._putlocal('x',X)
        self.session._putlocal('y',Y)
        whos = {'A':self.int, 'Z':Z, 'N':self.none, 'Q':Q, 'W':W, 'X':X, 'Y':Y}
        self.session._synclocal('a')
        self.assertEqual(all(self.array), all(self.session.whos['C']))
        self.session._poplocal('c')
        self.assertEqual(whos,self.session.whos)
        self.session._synclocal('c')
        whos['C'] = self.list #now is LIST, becuse _synclocal uses default 'get'
        self.assertEqual(whos,self.session.whos)
        self.assertRaises(NameError,self.session._synclocal,'f')
        self.assertEqual(whos,self.session.whos)
        self.assertRaises(AttributeError,self.session._synclocal,self.int)
        self.assertEqual(whos,self.session.whos)
        self.session._synclocal()
        whos = {'A':self.int, 'Z':Z, 'N':self.none, 'Q':Q, \
                'B':self.list, 'S':self.str}
        self.assertEqual(all(self.array), all(self.session.whos['C']))
        self.session.delete('c')
        self.assertEqual(whos,self.session.whos)
        return

    def test_IDLdelete(self):
        '''IDL: delete IDL variables'''
        self.session._putvar('a',self.int)
        self.session.put('b',self.list)
        self.session.put('c',self.array,array=True)
        self.session._putvar('n',self.none,allowNone=True)
        self.session._putvar('s',self.str)
        self.session.put('t',self.bytearray,array=True)
        self.session._putstringarr('u',self.strlist)
        self.assert_(self.session.delete("a") == None,
                     "failure to delete int")
        self.assert_(self.session.delete("b") == None,
                     "failure to delete list")
        self.assert_(self.session.delete("c") == None,
                     "failure to delete array")
        self.assert_(self.session.delete("n") == None,
                     "failure to delete None")
        self.assert_(self.session.delete("s") == None,
                     "failure to delete string")
        self.assert_(self.session.delete("t") == None,
                     "failure to delete bytearray")
        self.assert_(self.session.delete("u") == None,
                     "failure to delete strlist")
        self.assert_(self.session.delete("x") == None,
                     "failure to pass on delete of undefined")
        whos = {}
        self.assertEqual({},self.session.getbuff)
        self.assertEqual({},self.session.putbuff)
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertRaises(NameError,self.session.delete,'a, b')
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        return

    def test_IDLmap(self):
        '''IDL: get the IDL type mapping'''
        types = {3:'Int32', 1:'Int8', 2:'Int16', 'Int16':2, 4:'Float32',\
                 5:'Float64', 6:'Complex64', 'Int32':3, 'Float64':5,\
                 12:'UInt16', 'UInt8':1, 'Complex64':6, 'UInt16':12,\
                 'Int8':1, 'Float32':4}
       #self.assertEqual(types,self.session.map()) #FIXME: added types
       #self.assertEqual(3,self.session.map('Int32')) #Int64 on a64
       #self.assertEqual(3,self.session.map(Int32)) #Int64 on a64
        self.assertEqual('Int8',self.session.map(1))
        self.assertRaises(KeyError,self.session.map,'1')
        self.assertRaises(KeyError,self.session.map,100)
        self.assertRaises(TypeError,self.session.map,[1,2])
        return

    def test_IDLhelp(self):
        '''IDL: print the IDL help message'''
        self.assert_(self.session.help('a') == None,
                     "failure to print help for undefined variable")
        self.session._putvar('z',69)
        self.assert_(self.session.help('z') == None,
                     "failure to print help for known variable")
        self.assert_(self.session.help('a,z') == None,
                     "failure to print help for string sequence")
        self.assert_(self.session.help() == None,
                     "failure to print full help message")
        self.assertRaises(TypeError,self.session.help,1)
        return

    def test_IDLget(self):
        '''IDL: get a variable from IDL'''
        self.session.pyidl.eval("a = 1")
        self.session.pyidl.eval("s = 'foo'")
        whos = {'A':self.int, 'S':self.str}
        self.assertEqual(self.int,self.session.get('a'))
        self.assertEqual(self.str,self.session.get('s'))
        self.assertEqual(whos,self.session.who())
        self.assertEqual(whos,self.session.who(local=True))
        self.session.pyidl.eval("b = [1,2]")
        whos['B'] = self.list
        self.assertEqual(all(self.array),all(self.session.get('b',array=True)))
        self.assertEqual(all(self.array),all(self.session.who('b')))
        self.assertEqual(all(self.array),all(self.session.who('b',local=True)))
        self.assertEqual(self.list,self.session.get('b',array=False))
        self.assertEqual(whos,self.session.who())
        self.assertEqual(whos,self.session.who(local=True))
        #not exists
        self.assertRaises(NameError,self.session.get,'x')
        self.assertRaises(NameError,self.session.get,'n',allowNone=True)
        self.assertEqual(whos,self.session.who())
        self.assertEqual(whos,self.session.who(local=True))
        #None with exists
        self.session._putvar('n',self.none,allowNone=True)
        whos['N'] = self.none
        self.assertRaises(AttributeError,self.session.get,'n')
        self.assertEqual(whos,self.session.who())
        self.assertEqual(whos,self.session.who(local=True))
        #None with exists and allowNone
        self.assertEqual(self.none,self.session.get('n',allowNone=True))
        self.assertEqual(whos,self.session.who())
        self.assertEqual(whos,self.session.who(local=True))
        #STRING Arrays and BYTE Arrays
        self.session.pyidl.eval("t = BYTE(s)") #FIXME: testing for array=True?
        self.session.pyidl.eval("u = STRING(b)")
        whos['T'] = self.str
        whos['U'] = ['1', '2']
        self.assertEqual(self.str,self.session.get('t'))
        self.assertEqual(whos['U'],self.session.get('u'))
        self.assertEqual(whos,self.session.who())
        self.assertEqual(whos,self.session.who(local=True))
        return

    def test_IDLput(self):
        '''IDL: put a variable into IDL'''
        self.assert_(self.session.put("a",self.int) == None,
                     "failure to pass an int to IDL")
        self.assert_(self.session.put("b",self.list) == None,
                     "failure to pass a list to IDL")
        self.assert_(self.session.put("c",self.array) == None,
                     "failure to pass an array to IDL")
        self.assert_(self.session.put("s",self.str) == None,
                     "failure to pass a string to IDL")
        self.assert_(self.session.put("t",self.bytearray) == None,
                     "failure to pass a byte array to IDL")
        self.assert_(self.session.put("u",self.strlist) == None,
                     "failure to pass a string list to IDL")
        self.assertEqual(self.int, self.session.get('a'))
        self.assertEqual(self.int, self.session._getlocal('a'))
        self.assertEqual(self.list, self.session.get('b'))
        self.assertEqual(self.list, self.session._getlocal('b'))
        self.assertEqual(all(self.array), all(self.session.get('c')))
        self.assertEqual(all(self.array), all(self.session._getlocal('c')))
        self.assertEqual(self.session._checkarray('',self.array),\
                         self.session._checkarray('',self.session.get('c')))
        self.assertEqual(self.session._checkarray('',self.array),\
                         self.session._checkarray('',self.session.whos['C']))
        self.assertEqual(self.str, self.session.get('s'))
        self.assertEqual(self.str, self.session._getlocal('s'))
        self.assertEqual(all(self.bytearray), all(self.session.get('t')))
        self.assertEqual(all(self.bytearray), all(self.session._getlocal('t')))
        self.assertEqual(self.session._checkarray('',self.bytearray),\
                         self.session._checkarray('',self.session.get('t')))
        self.assertEqual(self.session._checkarray('',self.bytearray),\
                         self.session._checkarray('',self.session.whos['T']))
        self.assertEqual(self.strlist, self.session.get('u'))
        self.assertEqual(self.strlist, self.session._getlocal('u'))
        self.assertRaises(TypeError,self.session.put,'d',self.dict)
        self.assertRaises(ValueError,self.session.put,'n',self.none)
        whos = {'A':self.int, 'B':self.list, 'S':self.str}
        whos['U'] = self.strlist
        #now check how who & whos are affected...
        self.assertEqual(all(self.array), all(self.session.who('c')))
        self.assertEqual(all(self.array), all(self.session.who('c',local=True)))
        self.session.delete('C')
        self.assertEqual(all(self.bytearray), all(self.session.who('t')))
        self.assertEqual(all(self.bytearray),\
                         all(self.session.who('t',local=True)))
        self.session.delete('T')
        self.assertEqual(whos, self.session.who())
        self.assertEqual(whos, self.session.who(local=True))
        #allowNone
        self.assert_(self.session.put("n",self.none,allowNone=True) == None,
                     "failure to pass a None to IDL")
        self.assertEqual(self.none, self.session.get('n',allowNone=True))
        self.assertEqual(self.none, self.session._getlocal('n'))
        whos['N'] = self.none
        self.assertEqual(whos, self.session.who())
        self.assertEqual(whos, self.session.who(local=True))
        #specify array
        self.assert_(self.session.put("a",self.int,array=True) == None,
                     "failure to pass an int that ignores array to IDL")
        self.assertEqual(self.int, self.session.get('a'))
        self.assertEqual(self.int, self.session._getlocal('a'))
        self.assertEqual(self.int, self.session.who('a'))
        self.assertEqual(self.int, self.session.who('a',local=True))
        self.assert_(self.session.put("b",self.list,array=True) == None,
                     "failure to pass a list to IDL as array")
        self.assert_(self.session.put("c",self.array,array=False) == None,
                     "failure to pass an array to IDL as list")
        self.assert_(self.session.put("s",self.str,array=True) == None,
                     "failure to pass a string to IDL as BYTE Array")
        self.assert_(self.session.put("t",self.bytearray,array=False) == None,
                     "failure to pass a byte array to IDL STRING")
        b = self.session.pyidl.getvar('B')
        bb = self.session._processobj(b)
        self.assertEqual(all(self.array),all(bb))
        self.assertEqual(self.session._checkarray('',array(self.list)),\
                         self.session._checkarray('',bb))
        s = self.session.pyidl.getvar('S')
        ss = self.session._processobj(s)
        self.assertEqual(all(self.bytearray),all(ss))
        self.assertEqual(self.session._checkarray('',array(self.str)),\
                         self.session._checkarray('',ss))
        c = self.session.pyidl.getvar('C')
        self.assertEqual(self.list,self.session._processobj(c))
        t = self.session.pyidl.getvar('T')
        self.assertEqual(self.str,self.session._processobj(t))
        self.assertEqual(all(self.array), all(self.session._getlocal('b')))
        self.assertEqual(all(self.bytearray), all(self.session._getlocal('s')))
        self.assertEqual(self.list, self.session._getlocal('c'))
        self.assertEqual(self.str, self.session._getlocal('t'))
        self.assert_(self.session.put("u",self.strlist,array=True) == None,
                     "failure to pass an strlist that ignores array to IDL")
        self.assertEqual(self.strlist, self.session.get('u'))
        self.assertEqual(self.strlist, self.session._getlocal('u'))
        self.assertEqual(self.strlist, self.session.who('u'))
        self.assertEqual(self.strlist, self.session.who('u',local=True))
        #XXX: moved second half of test to pyIDLtest2.py
        return 

#       IO for subscripts TESTS NOT IMPLEMENTED
#       IO for pointer/object/heap TESTS NOT IMPLEMENTED
#       IO for structure TESTS NOT IMPLEMENTED

    def test_IDLwho(self):
        '''IDL: inquire who are the IDL variables'''
        self.session.pyidl.eval("a = 1")
        self.session.pyidl.eval("b = [1,2]")
        self.session.pyidl.eval("s = 'foo'")
        self.session.pyidl.eval("t = BYTE(s)")
        self.session.pyidl.eval("u = STRING(b)")
        whos = {'A':self.int, 'B':self.list, 'S':self.str, 'T':self.str}
        whos['U'] = ['1','2']
        self.assertEqual(self.int,self.session.who('a'))
        self.assertEqual(self.list,self.session.who('b'))
        self.assertEqual(self.str,self.session.who('s'))
        self.assertEqual(self.str,self.session.who('t'))
        self.assertEqual(whos['U'],self.session.who('u'))
        self.assertEqual(whos,self.session.who())
        whos['N'] = self.none
        self.session.put('n',None,allowNone=True)
        self.assertEqual(self.none,self.session.who('n'))
        self.assertEqual(whos,self.session.who())
        #local changes
        self.session._putlocal('a',self.list)
        self.session._putlocal('b',self.str)
        self.session._putlocal('c',self.int)
        self.session._putlocal('n',self.str)
        self.session._putlocal('s',self.int)
        self.assertEqual(self.list,self.session.who('a',local=True))
        self.assertEqual(self.str,self.session.who('b',local=True))
        self.assertEqual(self.int,self.session.who('c',local=True))
        self.assertEqual(self.str,self.session.who('n',local=True))
        self.assertEqual(self.int,self.session.who('s',local=True))
        self.assertEqual(self.str,self.session.who('t',local=True))
        self.assertEqual(whos['U'],self.session.who('u',local=True))
        self.session._poplocal('b')
        self.assertRaises(NameError,self.session.who,'b',local=True)
        self.assertEqual(whos,self.session.who())
        self.assertEqual(whos,self.session.who(local=True))
        #failures
        self.assertRaises(NameError,self.session.who,'x')
        self.assertRaises(NameError,self.session.who,'a, b') #XXX: allow this?
        self.assertEqual(whos,self.session.who())
        self.assertEqual(whos,self.session.who(local=True))
        #stdout #XXX: remember IDL stdout is shut off...
        self.assert_(self.session.who('a',stdout=True) == None,
                     "failure to print IDL who for int")
#       self.assert_(self.session.who('a',local=True,stdout=True) == None,
#                    "failure to print local who for int")
        self.assert_(self.session.who(stdout=True) == None,
                     "failure to print IDL who")
#       self.assert_(self.session.who(local=True,stdout=True) == None,
#                    "failure to print local who")
        return

    def test_IDL_processIDLcommand(self):
        '''IDL: preprocess ';' and '$ in IDL command'''
        command = ''
        self.assertEqual(command,self.session._processIDLcommand(command))
        command = 'foo'
        self.assertEqual(command,self.session._processIDLcommand(command))
        command = 's = foo'
        self.assertEqual(command,self.session._processIDLcommand(command))
        command = 's = "foo"'
        self.assertEqual(command,self.session._processIDLcommand(command))
        command = "s = 'foo'"
        self.assertEqual(command,self.session._processIDLcommand(command))
        command = 'foo$'
        self.assertEqual(command,self.session._processIDLcommand(command))
        command = 'foo;'
        self.assertEqual('foo',self.session._processIDLcommand(command))
        command = 'foo$$'
        self.assertEqual('foo$',self.session._processIDLcommand(command))
        command = 'foo;;'
        self.assertEqual('foo',self.session._processIDLcommand(command))
        command = 'foo$bar'
        self.assertEqual('foo$',self.session._processIDLcommand(command))
        command = 'foo;bar'
        self.assertEqual('foo',self.session._processIDLcommand(command))
        command = 'foo$bar;'
        self.assertEqual('foo$',self.session._processIDLcommand(command))
        command = 'foo;bar$'
        self.assertEqual('foo',self.session._processIDLcommand(command))
        command = 'foo$bar$'
        self.assertEqual('foo$',self.session._processIDLcommand(command))
        command = 'foo;bar;'
        self.assertEqual('foo',self.session._processIDLcommand(command))
        #comments
        command = ';'
        self.assertEqual(None,self.session._processIDLcommand(command))
        command = ';foo'
        self.assertEqual(None,self.session._processIDLcommand(command))
        command = ';foo$'
        self.assertEqual(None,self.session._processIDLcommand(command))
        command = ';foo$bar'
        self.assertEqual(None,self.session._processIDLcommand(command))
        command = ';foo;bar'
        self.assertEqual(None,self.session._processIDLcommand(command))
        #os commands
        self.session.evalbuff = []
        command = '$'
        self.assertEqual(command,self.session._processIDLcommand(command))
        self.session.evalbuff = []
        command = '$foo'
        self.assertEqual(command,self.session._processIDLcommand(command))
        self.session.evalbuff = []
        command = '$foo$'
        self.assertEqual(command,self.session._processIDLcommand(command))
        self.session.evalbuff = []
        command = '$foo$bar'
        self.assertEqual(command,self.session._processIDLcommand(command))
        self.session.evalbuff = []
        command = '$foo;bar'
        self.assertEqual(command,self.session._processIDLcommand(command))
        #NOT os commands, but comments
        self.session.evalbuff = ['X']
        command = '$'
        self.assertEqual('$',self.session._processIDLcommand(command))
        self.session.evalbuff = ['X']
        command = '$foo'
        self.assertEqual('$',self.session._processIDLcommand(command))
        self.session.evalbuff = ['X']
        command = '$foo$'
        self.assertEqual('$',self.session._processIDLcommand(command))
        self.session.evalbuff = ['X']
        command = '$foo$bar'
        self.assertEqual('$',self.session._processIDLcommand(command))
        self.session.evalbuff = ['X']
        command = '$foo;bar'
        self.assertEqual('$',self.session._processIDLcommand(command))
        #leading whitespace
        command = ' '
        self.assertEqual(command,self.session._processIDLcommand(command))
        command = ' foo'
        self.assertEqual(command,self.session._processIDLcommand(command))
        command = ' ;foo'
        self.assertEqual(None,self.session._processIDLcommand(command))
        self.session.evalbuff = []
        command = ' $foo'
        self.assertEqual(command,self.session._processIDLcommand(command))
        self.session.evalbuff = ['X']
        command = ' $foo'
        self.assertEqual(' $',self.session._processIDLcommand(command))
        return

    def test_IDL_putevalbuff(self):
        '''IDL: add a command to the evalbuff'''
        evalbuff = []
        self.assertEqual(evalbuff,self.session.evalbuff)
        self.assert_(self.session._putevalbuff('a = 1') == None,
                     "failure to add to empty evalbuff")
        evalbuff.append('a = 1')
        self.assertEqual(evalbuff,self.session.evalbuff)
        self.assert_(self.session._putevalbuff('$fo;o') == None,
                     "failure to add to evalbuff unaffected by $ and ;")
        evalbuff.append('$fo;o')
        self.assertEqual(evalbuff,self.session.evalbuff)
        self.assert_(self.session._putevalbuff('hello = $') == None,
                     "failure to add to evalbuff unaffected by $ continue")
        evalbuff.append('hello = $')
        self.assertEqual(evalbuff,self.session.evalbuff)
        return

    def test_IDL_processIDLbuff(self):
        '''IDL: process the evalbuff for execution'''
        self.session.evalbuff = ['exit']
        self.assertEqual('exit',self.session._processevalbuff())
        self.assertEqual([],self.session.evalbuff)
        self.session.evalbuff = ['']
        self.assertEqual('',self.session._processevalbuff())
        self.assertEqual([],self.session.evalbuff)
        self.session.evalbuff = ['a = 1']
        self.assertEqual('a = 1',self.session._processevalbuff())
        self.assertEqual([],self.session.evalbuff)
        self.session.evalbuff = ['a = ','','1']
        self.assertEqual('a =   1',self.session._processevalbuff())
        self.assertEqual([],self.session.evalbuff)
        self.session.evalbuff = ['a = $','a & b = $','2']
        self.assertEqual('a = $ a & b = $ 2',self.session._processevalbuff())
        self.assertEqual([],self.session.evalbuff)
        self.session.evalbuff = []
        self.assertEqual(None,self.session._processevalbuff())
        self.assertEqual([],self.session.evalbuff)
        self.session.evalbuff = ['a = $']
        self.assertEqual(None,self.session._processevalbuff())
        self.assertEqual(['a = '],self.session.evalbuff)
        self.session.evalbuff = ['a = $','','$']
        self.assertEqual(None,self.session._processevalbuff())
        self.assertEqual(['a = $','',''],self.session.evalbuff)
        self.session.evalbuff = ['$']
        self.assertEqual('$',self.session._processevalbuff())
        self.assertEqual([],self.session.evalbuff)
        self.session.evalbuff = ['  $']
        self.assertEqual('$',self.session._processevalbuff())
        self.assertEqual([],self.session.evalbuff)
        self.session.evalbuff = ['$foo']
        self.assertEqual('$foo',self.session._processevalbuff())
        self.assertEqual([],self.session.evalbuff)
        self.session.evalbuff = ['$','$']
        self.assertEqual(None,self.session._processevalbuff())
        self.assertEqual(['$',''],self.session.evalbuff)
        return

#   def test_IDL_validateexpr(self): #FIXME
#       '''IDL: validate an IDL expression'''
#       return

    def test_IDL_isexpr(self): #FIXME this could be much better...
        '''IDL: check if includes form of valid IDL subexpression'''
        self.assertEqual(False,self.session._isexpr('b'))
        self.assertEqual(False,self.session._isexpr('[]'))
        self.assertEqual(False,self.session._isexpr('[b]'))
        self.assertEqual(False,self.session._isexpr('b[]'))
        self.assertEqual(True,self.session._isexpr('b[0]'))
        self.assertEqual(True,self.session._isexpr('b[c]'))
#       self.assertEqual(False,self.session._isexpr('b[c[]]'))
        self.assertEqual(True,self.session._isexpr('b[c[0]]'))
        self.assertEqual(False,self.session._isexpr('b + d'))
        self.assertEqual(True,self.session._isexpr('b[c] + d'))
        self.assertEqual(True,self.session._isexpr('a[b + d]'))
        self.assertEqual(True,self.session._isexpr('a[b[c] + d[e]]'))
        self.assertEqual(True,self.session._isexpr('()'))
        self.assertEqual(True,self.session._isexpr('(b)'))
        self.assertEqual(True,self.session._isexpr('b()'))
        self.assertEqual(True,self.session._isexpr('b(0)'))
        self.assertEqual(True,self.session._isexpr('b(c)'))
        self.assertEqual(True,self.session._isexpr('b(c())'))
        self.assertEqual(True,self.session._isexpr('b(c(0))'))
        self.assertEqual(False,self.session._isexpr('b + d'))
        self.assertEqual(True,self.session._isexpr('b(c) + d'))
        self.assertEqual(True,self.session._isexpr('a(b + d)'))
        self.assertEqual(True,self.session._isexpr('a(b(c) + d(e))'))
        return

    def test_IDL_exprroot(self):
        '''IDL: get the roots of an IDL expression'''
        self.assertEqual(['b'],self.session._exprroot('b[1]'))
        self.assertEqual(['b'],self.session._exprroot('b[1,0]'))
        self.assertEqual(['b'],self.session._exprroot('b[1,0,0]'))
        self.assertEqual(['b'],self.session._exprroot('b[0:0]'))
        self.assertEqual(['b'],self.session._exprroot('b[0:1]'))
        self.assertEqual(['b'],self.session._exprroot('(b[0:1])[*]'))
        self.assertEqual(['b'],self.session._exprroot('b[*]'))
        self.assertEqual(['b'],self.session._exprroot('b[0:*]'))
        self.assertEqual(['b'],self.session._exprroot('b[1:*]'))
        self.assertEqual(['b'],self.session._exprroot('b[*:0]'))
        self.assertEqual(['b'],self.session._exprroot('b[0:6]'))
        self.assertEqual(['b'],self.session._exprroot('b[0,[0:1]]'))
        self.assertEqual(['b'],self.session._exprroot('b['))
        self.assertEqual(['x'],self.session._exprroot('x['))
        self.assertEqual(['x'],self.session._exprroot('x[0]'))
        expr = '1+a +(sin(x) + (foo(y))[0]) + f*exp((c[b:100-n])[0])'
        roots = ['a','x','y','f','c','b','n']
        self.assertEqual(roots,self.session._exprroot(expr))
        expr = 'IF ++a GT b[0]'
        roots = ['a','b']
        self.assertEqual(roots,self.session._exprroot(expr))
        self.assertEqual([],self.session._exprroot(expr,allowUndefined=False))
        self.session.put('a',self.int)
        self.session.put('b',self.list)
        self.session.put('n',self.none,allowNone=True)
        self.session.put('s',self.str)
        expr = '1+a +(sin(x) + (foo(y))[0]) + f*exp((c[b:100-n])[0])'
        ok = ['a','b','n']
        self.assertEqual(ok,self.session._exprroot(expr,allowUndefined=False))
        return

    def test_IDL_sortexists(self):
        '''IDL: sort variable namelist into existing and non-existing'''
        self.session.put('a',self.int)
        self.session.put('b',self.list)
        self.session.put('n',self.none,allowNone=True)
        self.session.put('s',self.str)
        self.session.put('u',self.strlist)
        varlist = ['a','b','n','s','u']
        self.assertEqual((varlist,[]),self.session._sortexists(varlist))
        mixlist = ['e','ab','r','a','b']
        self.assertEqual((['a','b'],['e','ab','r']),\
                         self.session._sortexists(mixlist))
        nonelist = ['e','ab','r']
        self.assertEqual(([],nonelist),self.session._sortexists(nonelist))
        self.assertEqual(([],[]),self.session._sortexists([]))
        self.assertRaises(TypeError,self.session._sortexists,'abnsu')
        self.assertRaises(TypeError,self.session._sortexists,self.int)
        self.assertRaises(AttributeError,self.session._sortexists,self.list)
        return

    #FIXME: add testing using matrix!
    def test_IDL_getexpr(self): #FIXME: finish testing; add keyword tests?
        '''IDL: get the value of an IDL expression'''
        A = self.int #(non-array)
        B = self.list
        D = self.dict
        M = self.matrix
        N = self.none
        S = self.str
        T = self.bytearray
        U = self.strlist
        whos = {'B':B }
        self.session.put('b',self.list)
        self.assertEqual(B[1],self.session._getexpr('b[1]'))
        self.assertEqual(B[1],self.session._getexpr('b[1,0]'))
        self.assertEqual(B[1],self.session._getexpr('b[1,0,0]'))
        self.assertEqual([B[0]],self.session._getexpr('b[0:0]'))
        self.assertEqual(B,self.session._getexpr('b[0:1]'))
        self.assertEqual(B,self.session._getexpr('(b[0:1])[*]'))
        self.assertEqual(B,self.session._getexpr('b[*]'))
        self.assertEqual(B,self.session._getexpr('b[0:*]'))
        self.assertEqual([B[1]],self.session._getexpr('b[1:*]'))
        #self.assertEqual([1,1],self.session._getexpr('b[0,[1,0]]')) #[[1,1]]
        self.assertEqual(whos,self.session.whos)
        #failures #FIXME: need standardization of Errors
        #'''
        self.assertRaises(AttributeError,self.session._getexpr,'b[*:0]')
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertRaises(AttributeError,self.session._getexpr,'b[0:6]')
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
# XXX   self.assertRaises(AttributeError,self.session._getexpr,'b[0,[0:1]]')
        self.assertRaises(NameError,self.session._getexpr,'b[0,[0:1]]')
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
# XXX   self.assertRaises(AttributeError,self.session._getexpr,'b[')
        self.assertRaises(NameError,self.session._getexpr,'b[')
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
# XXX   self.assertRaises(AttributeError,self.session._getexpr,'x[')
        self.assertRaises(NameError,self.session._getexpr,'x[')
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
# XXX   self.assertRaises(NameError,self.session._getexpr,'x[0]')
        self.assertRaises(AttributeError,self.session._getexpr,'x[0]')
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
#'''
        return

    def test_IDL_putexpr(self): #FIXME: add testing using matrix!
        '''IDL: put a value into IDL as part of an IDL expression'''
        A = self.int #(non-array)
        B = self.list
        D = self.dict
        M = self.matrix
        N = self.none
        S = self.str
        T = self.bytearray
        U = self.strlist
        whos = {'B':B }
        self.session.put('b',B)
        whos['B'] = [6,6]
        self.assertEqual(None,self.session._putexpr('b[0:1]',6))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        whos['B'][1] = 9
        self.assertEqual(None,self.session._putexpr('b[1]',9))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        whos['B'][0] = 0
        self.assertEqual(None,self.session._putexpr('b[0:0]',0))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        whos['B'] = [1,2]
        self.assertEqual(None,self.session._putexpr('b[0:1]',[1,2]))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        whos['B'] = [1,2]
        self.assertEqual(None,self.session._putexpr('b[*]',[1,2]))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        whos['B'] = [3,4]
        self.assertEqual(None,self.session._putexpr('b[0:*]',[3,4]))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        whos['B'][1] = 2
        self.assertEqual(None,self.session._putexpr('b[1:*]',2))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        whos['B'][0] = 1
        self.assertEqual(None,self.session._putexpr('b[0,[1,0]]',1))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        #failures name #FIXME: need Errors? standardization?
        #'''
        #XXX: raise AttributeError for IDL syntax error ?
        self.assertEqual(None,self.session._putexpr('b[1,0]',[0,1]))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertEqual(None,self.session._putexpr('b[1,0,0]',[1,2]))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertEqual(None,self.session._putexpr('(b[0:1])[*]',[6,9]))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertEqual(None,self.session._putexpr('b[*:0]',0))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertEqual(None,self.session._putexpr('b[0:6]',[1,2]))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertEqual(None,self.session._putexpr('b[0,[0:1]]',0))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertEqual(None,self.session._putexpr('b[',[1,2]))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertEqual(None,self.session._putexpr('x[',[1,2]))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertEqual(None,self.session._putexpr('x[0]+y[0]',0))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        #XXX: raise NameError on IDL undefined ?
        self.assertEqual(None,self.session._putexpr('x[0]',0))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        #failures value
        self.assertEqual(None,self.session._putexpr('b[1]',[3,4]))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertEqual(None,self.session._putexpr('b[1:1]',[3,4]))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertEqual(None,self.session._putexpr('b[*]',[0,3,4]))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertRaises(TypeError,self.session._putexpr,'b[0]',D)
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertEqual(None,self.session._putexpr('b[0]',M))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        self.assertEqual(None,self.session._putexpr('b[0]',N,allowNone=True))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        whos['B'][0] = 0 #IDL Type conversion error causes to be set to 0
        self.assertEqual(None,self.session._putexpr('b[0]',S))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
        whos['B'][1] = 0 #IDL Type conversion error causes to be set to 0
        self.assertEqual(None,self.session._putexpr('b[0]',U))
        self.assertEqual(whos,self.session.whos)
        self.assertEqual(whos,self.session.who())
#'''
        return

#   def test_IDLeval(self):
#       return

#   def test_IDLprompt(self):
#       #same as all 'eval'?
#       return

### TESTING USE CASES FOR EVAL ###

    def test_IDLevalIDLassign(self):
        '''IDL: evaluate an IDL assignment expression'''
        self.assert_(self.session.eval("a = 1") == None,
                     "failure to eval an int")
        self.assert_(self.session.eval("b = [1,2]") == None,
                     "failure to eval a vector")
        self.assert_(self.session.eval("c = [[1,2],[3,4]]") == None,
                     "failure to eval a 2D matrix")
        self.assert_(self.session.eval("d = !PI") == None,
                     "failure to eval a reserved expression")
        self.assert_(self.session.eval("e = b ## c") == None,
                     "failure to eval IDL matrix operation")
        self.assert_(self.session.eval("g = sin(0)") == None,
                     "failure to eval a scalar expression")
        self.assert_(self.session.eval("h = indgen(3)") == None,
                     "failure to eval an array expression")
        self.assert_(self.session.eval("n = n") == None,
                     "failure to eval an IDL None")
        self.assert_(self.session.eval("s = 'foo'") == None,
                     "failure to eval a 1D string")
        whos = {'A':1, 'C':[[1,2],[3,4]], 'B':[1,2], 'E':[7,10], 'S':'foo',
                'D':3.1415927410125732, 'G':0.0, 'H':[0,1,2], 'N':None}
        self.assertEqual(whos, self.session.who(local=True))
        self.assertEqual(whos, self.session.who())
        return #FIXME: add BYTE Array & STRING Array

    def test_IDLevalIDLmanip(self):
        '''IDL: evaluate an IDL modification expression'''
        self.session.eval('a = 1')
        self.session.eval('b = [1,2]')
        self.session.eval("c = [[1,2],[3,4]]")
        self.assert_(self.session.eval("a += 1") == None,
                     "failure to eval compound assignment")
        self.assert_(self.session.eval("a++") == None,
                     "failure to eval increment operator")
        self.assert_(self.session.eval("b(1) = 0") == None,
                     "failure to eval obsolete array notation")
        self.assert_(self.session.eval("c[0] = 4") == None,
                     "failure to eval array notation")
        self.assert_(self.session.eval("c[1,1] = 1") == None,
                     "failure to eval matrix notation")
        self.assert_(self.session.eval("c[1:2] = [3,2]") == None,
                     "failure to eval slice notation")
        whos = {'A': 3, 'C': [[4,3],[2,1]], 'B': [1,0]}
        self.assertEqual(whos, self.session.who(local=True))
        self.assertEqual(whos, self.session.who())
        return

    def test_IDLevaldelvar(self):
        '''IDL: delete an IDL variable upon 'delvar' command'''
        self.session.eval("a = 1")
        self.session.eval("b = 2")
        self.session.eval("c = [1,2]")
        self.assert_(self.session.eval("delvar, b, c") == None,
                     "failure to perform 'delvar' command")
        self.session.eval("d = d")
        self.assert_(self.session.eval("delvar, d") == None,
                     "failure to 'delvar' an undefined variable")
        whos = {'A': 1}
        self.session.eval("s = foo()")
        self.session.eval("s = t")
        self.session.eval("u[0] = 1")
        whos['S'] = None
        whos['T'] = None
        whos['U'] = None
        self.assertEqual(whos, self.session.who(local=True))
        self.assertEqual(whos, self.session.who())
        return

    def test_IDLevalexit(self):
        '''IDL: do nothing upon 'exit' command'''
        self.session.eval('a = 1')
        self.assert_(self.session.eval("exit") == None,
                     "failure to skip 'exit' command")
        whos = {'A': 1}
        self.assertEqual(whos, self.session.who(local=True))
        self.assertEqual(whos, self.session.who())
        return

    def test_IDLevalIDLconditional(self):
        '''IDL: evaluate an IDL conditional expression'''
        self.session.eval('a = 1')
        self.assert_(self.session.eval(\
                     "IF (a LT 100) THEN a += 1 ELSE a = 0") == None,
                     "failure to eval conditional expression")
        self.assert_(self.session.eval("a = (a GT 100) ? 0 : a + 1") == None,
                     "failure to eval ternary expression")
        whos = {'A': 3}
        self.assertEqual(whos, self.session.who(local=True))
        self.assertEqual(whos, self.session.who())
        return

#   def test_IDLevalIDLfunction(self):
#       '''IDL: eval procedure/function/commonblock TESTS NOT IMPLEMENTED'''
#       pass

#   def test_IDLevalIDLheap(self):
#       '''IDL: eval pointer/object/heap TESTS NOT IMPLEMENTED'''
#       pass

#   def test_IDLevalIDLstruct(self):
#       '''IDL: eval structure TESTS NOT IMPLEMENTED'''
#       pass

#   def test_IDLevalIDLmultiline(self):
#       '''IDL: eval multiline/continuation/compound TESTS NOT IMPLEMENTED'''
#       pass

#   def test_IDLevalIDLoscommand(self):
#       '''IDL: eval os command TESTS NOT IMPLEMENTED'''
#       pass

#   def test_IDLevalpython(self):
#       '''IDL: fail upon a python expression'''
#       pass

#   def test_IDLprompt(self):
#       '''IDL: prompt TESTS NOT IMPLEMENTED'''
#       pass


if __name__ == "__main__":
    suite0 = unittest.makeSuite(PyIDL_rsiIDL_TestCase)
    alltests = unittest.TestSuite((suite0,))
    unittest.TextTestRunner(verbosity=2).run(alltests)


#  End of file 
