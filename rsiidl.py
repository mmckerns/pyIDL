#!/usr/bin/env python
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# 03/05/2009 version 0.7
# mmckerns@caltech.edu
# (C) 2005-2009 All Rights Reserved
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
__license__ = """
This software is part of the open-source DANSE project at the California
Institute of Technology, and is available subject to the conditions and terms
laid out below. By downloading and using this software you are agreeing to the
following conditions.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistribution of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

    * Redistribution in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentations
and/or other materials provided with the distribution.

    * Neither the name of the California Institute of Technology nor the names
of its contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Copyright (c) 2009 California Institute of Technology. All rights reserved.


If you use this software to do productive scientific research that leads to
publication, we ask that you acknowledge use of the software by citing the
following paper in your publication:

    "pyIDL: binding IDL to python", Michael McKerns, unpublished;
     http://www.cacr.caltech.edu/~mmckerns/software.html

"""


__author__='Mike McKerns'
__doc__= """
pyIDL: Python-IDL bindings
    instantiate: ri = pyIDL.idl()
    usage: print ri.doc()
"""
#TODO: local store should NOT hold duplicate copies of IDL arrays if possible.
#      a much better approach would be to hold the buffer handle, and any
#      pertaining information like 'array' & 'type'.
#TODO: use 'obj.getitem and obj.setitem from PyC bindings ?
#TODO: pyC bindings should use numpy/numarray C-API, not mapping hackery
#TODO: upgrade numarray dependency to numpy (or at least numpy.numarray
#FIXME: bad window behavior -- plot needs 'resetting' when called repeatedly
#FIXME: (examples) throw EOFError after few seconds when script has "raw_input"

import _pyIDL
import numarray
from numarray import strings as numstring

try:
    from numpy import ndarray
    hasnumpy = True
except ImportError:
    hasnumpy = False
try:
    from Numeric import ArrayType
    hasnumeric = True
except ImportError:
    hasnumeric = False


#set platform specific code strings...
from sys import platform
if platform[:3] == 'win':
    sep = 'STRING(13b)+STRING(10b)'
elif platform[:3] == 'mac':
    sep = 'STRING(13b)'
else: #unix/linux
    sep = 'STRING(10b)'

class IDLProc:
    def __init__(self,name,klass,func='?'):
        if func == '?':
            func = klass._isIDLfunc(str(name))
        self._klass = klass
        self.name = name
        self.func = func
        self.tmp = "pyfn1m2n3b4v"
        self.tmp2 = 'm1n2b3v4_'
        self.num_args = 0

    def arg_to_string(self, arg):
        if hasnumeric:
            if isinstance(arg, ArrayType):
                arg = numarray.array(arg)
        if hasnumpy:
            if isinstance(arg, ndarray):
                arg = numarray.array(arg)
        if isinstance(arg, numarray.NumArray):
            name = self.tmp+str(self.num_args)
            ishape = self._klass._invertshape(arg._shape)
            itype = self._klass.types[arg._type]
            na = _pyIDL.setarr(name,arg._data,itype,ishape)
            self.reserve.append(na)
            self.num_args += 1
            return na.name()
        return repr(arg)

    def make_call_string(self,args,kwds):
        argv = [self.name]
        for arg in args:
            argv.append(self.arg_to_string(arg))
        for (key,arg) in kwds.iteritems():
            if isinstance(arg,bool):         # for booleans
                if arg: argv.append("/"+key) # True  == "/arg" 
                else: pass                   # False == ""
            else: argv.append(key+"="+self.arg_to_string(arg))
        if self.func:
            cmd = self.tmp+" = "+self.name+"("+", ".join(argv[1:])+")"
        else:
            cmd = ", ".join(argv)
        return cmd

    def __call__(self, *args, **kwds):
        self.num_args = 0
        self.reserve = []
        _pyIDL.eval(self.make_call_string(args,kwds))
        self.reserve = []
        self.num_args = 0
        self._klass.delete(self.name) #FIXME: deletes user-defined pro!
        if self.func:
            ans = self._klass.get(self.tmp)
            self._klass.delete(self.tmp)
            return ans

class idlpro:
    '''interface to IDL procedures/functions'''
    def __init__(self,klass):
        self._klass = klass
        return

    def __getattr__(self,name):
        if name is '_print':
            name = 'print'
        return IDLProc(name,self._klass)

class idl:
    """
idl: Python-IDL bindings
    eval(command):
        execute an IDL command
    get(name,[array,allowNone]):
        fetch a variable from IDL
    put(name,value,[array,type,allowNone]):
        push a variable to IDL
    who([name,local,stdout]):
        print/return the IDL/local variables
    help([name]):
        print the IDL help message (for a variable)
    delete(name):
        destroy selected IDL variables
    map([name]):
        get the IDL data type mapping
    prompt():
        an interactive IDL session
    _print(value):
        print using the IDL print command"""
    _privdoc="""
private methods:
    _validate:
        raise NameError if invalid name
    _validatestore:
        check if store is a valid dictionary
    _putlocal:
        add a variable to local store
    _getlocal:
        return variable value from local store
    _poplocal:
        delete variable from local store, return value
    _islist:
        True if self.whos[name] is a list
    _isarray:
        True if self.whos[name] is a NumArray
    _ischararray:
        True if self.whos[name] is a CharArray
    _toarray:
        T/F validated against the default
    _totype:
        get type if self.whos[name] is a NumArray
    _prolist:
        get a list of strings containing all IDL procedures
    _funclist:
        get a list of strings containing all IDL functions
    _wholist:
        get a list of strings containing all IDL variables
    _exists:
        True if is a variable in IDL
    _isIDLfunc:
        True if is an IDL function'''
    _isIDLpro:
        True if is an IDL procedure'''
    _isarrayobj:
        True if is an IDL_Array obj
    _invertshape:
        translate shape between IDL and NumArray
    _putstringarr:
        put list of strings as STRING Array
    _processstringarrayobj:
        get IDL string array as a list
    _processobj:
        extract value from IDL_array obj
    _putvar:
        put a scalar into IDL
    _checkarray:
        set (array,type) for _put
    _delarr:
        clears named obj from getbuff & putbuff
    _synclocal:
        update local store value to IDL value
    _processIDLcommand:
        preprocess ';' and '$' in command
    _putevalbuff:
        add command to evalbuff
    _processevalbuff:
        prepare evalbuff as a single IDL command
    _isexpr:
        True if includes valid form of IDL subexpression
    _exprroot:
        extract root variables
    _sortexists:
        sort list into existing (and non-)
    _putexpr:
        set array portion
    _getexpr:
        get array portion"""

    def __init__(self,stdout=True):
        '''start a simple IDL session'''
        _pyIDL.open(stdout)
        self.pyidl = _pyIDL
        self.types = self.pyidl.getmap(numarray)
        self.pros = idlpro(self)
        self.whos = {}
        self.getbuff = {}
        self.putbuff = {}
        self.evalbuff = []
        self.special = ['!',';','$','&',':','@','?'] #also ["'",'"','*','.']
        self.reserved = ['AND','BEGIN','BREAK','CASE','COMMON','COMPILE_OPT',
                         'CONTINUE','DO','ELSE','END','ENDCASE','ENDELSE',
                         'ENDFOR','ENDIF','ENDREP','ENDSWITCH','ENDWHILE',
                         'EQ','FOR','FORWARD_FUNCTION','FUNCTION','GE',
                         'GOTO','GT','IF','INHERITS','LE','LT','MOD','NE',
                         'NOT','OF','ON_IOERROR','OR','PRO','REPEAT','SWITCH',
                         'THEN','UNTIL','WHILE','XOR']
        self.operator1 = ['*','^','++','--','##','#','/','+','-','<','>',
                          '&&','||','~','?:'] #also ['.']
        self.operator2 = ['(',')','[',']']
        self.operator3 = [',',':','*']
        self.operator4 = ['MOD','NOT','EQ','NE','LE','LT','GE','GT','AND',
                          'OR','XOR']
        return

    def __del__(self):
        '''end a simple IDL session'''
#       self.pyidl.close()                     #kills idl & python
        self.pyidl.eval(".full_reset_session") #destroys vars + plots + DLM
#       self.pyidl.eval(".reset_session")      #destroys vars + plots
#       self.pyidl.eval("wdelete")             #destroys plots only
        self.pyidl = None                      #destroys vars only
        return

    def __getattr__(self,name):
        attr = None
        try:
            exec 'attr = self.get("'+name+'")'
        except:
            exec 'attr = self.pros.'+name
        return attr

    def __setattr__(self,name,value):
        if name in ['pyidl','types','pros','whos','getbuff',
                    'putbuff','evalbuff','special','reserved',
                    'operator1','operator2','operator3','operator4']:
            #XXX: all attributes set in __init__ *must* be listed above
            self.__dict__[name] = value
            return
        #pass into IDL as a variable
        self.put(name,value)
        return

    def __call__(self,*args):
        for arg in args:
            self.eval(arg)
        return

    def _validate(self,name):
        '''_validate(name) --> raise NameError if invalid name'''
        #a valid IDL name begins with a letter, and can include only
        #alphanumeric symbols along with the underscore and dollar sign.
        #IDL also does not allow redefinition of reserved words.
        #FIXME: python does not allow the dollar sign in variable names
        if not name: raise NameError, "invalid name '%s'" % name
        import re
        if re.compile('[a-zA-Z]').sub('',name[0]):
            raise NameError, "invalid first character '%s'" % name[0]
        #badc = re.compile('[_a-zA-Z0-9]').sub('',name) #'$' invalid in python
        badc = re.compile('[_$a-zA-Z0-9]').sub('',name)
        if badc: raise NameError, "invalid name '%s'; remove '%s'" % (name,badc)
        if name.upper() in self.reserved:
            raise NameError, "invalid name '%s'; is an IDL reserved word" % name
        return

    def _validatestore(self,store):
        '''_validatestore(store) --> check if store is a valid dictionary'''
        if str(store) not in ['whos','getbuff','putbuff']:
            raise NameError, "invalid store '%s'" % str(store)
#       try: exec "valid = isinstance("+str(store)+",dict)"
#       except: raise TypeError, "invalid store '%s'" % str(store)
#       if not valid: raise NameError, "invalid store '%s'" % str(store)
        return

    def _putlocal(self,name,value,store=None):
        '''_putlocal(name,value) --> add a variable to local store'''
        self._validate(name)
        if store is None: store = 'whos'
        self._validatestore(store)
        exec "self."+str(store)+"[name.upper()] = value"
        return

    def _getlocal(self,name,store=None,skip=True):
        '''_getlocal(name) --> return variable value from local store'''
        name = name.upper()
        if store is None: store = 'whos'
        self._validatestore(store)
        exec "haskey = self."+str(store)+".has_key(name)"
        if not haskey:
            if skip: return
            raise NameError,"'%s' is not defined in %s" % (str(name),str(store))
        exec "value = self."+str(store)+"[name]"
        return value

    def _poplocal(self,name,store=None):
        '''_poplocal(name) --> delete variable from local store, return value'''
        if store is None: store = 'whos'      #default: 'local' delete only
        self._validatestore(store)            #delete in *buff kills IDL arrays
        exec "value = self."+store+".pop(name.upper(),None)"
        return value

    def _islist(self,name):
        '''_islist(name) --> True if self.whos[name] is a list'''
        if isinstance(self._getlocal(name),list): return True
        return False

    def _isarray(self,name):
        '''_isarray(name) --> True if self.whos[name] is a NumArray'''
        if isinstance(self._getlocal(name),numarray.NumArray): return True
        return False

    def _ischararray(self,name):
        '''_ischararray(name) --> True if self.whos[name] is a CharArray'''
        if isinstance(self._getlocal(name),numstring.CharArray): return True
        return False

    def _toarray(self,name,default='list'):
        '''_toarray(name,[default]) --> T/F validated against the default''' 
        if default not in ['array', 'NumArray', 'numarray',\
                           'numarray.array', 'numarray.NumArray']:
            if self._isarray(name): return True
            return False #default: convert to LIST/STRING
        if self._islist(name): return False
        return True #default: convert to NumArray

    def _totype(self,name):
        '''_totype(name) --> get type if self.whos[name] is a NumArray'''
        if not self._isarray(name): return None
        return self._getlocal(name).type()

    def _prolist(self):
        '''_prolist() --> get a list of strings containing all IDL procedures'''
        tmp = 'p0o9i8u7y6'
        self.pyidl.eval(tmp+" = '"+tmp+"'")
        self.pyidl.eval(tmp+" = ROUTINE_NAMES(/S_PROCEDURES)")
        #self.pyidl.eval(tmp+" = ROUTINE_NAMES(/PROCEDURES, /UNRESOLVED)")
        self.pyidl.eval(tmp+" = STRJOIN("+tmp+", "+sep+")") 
        prolist = self.pyidl.getvar(tmp).split()
        self.delete(tmp)
        return prolist

    def _funclist(self):
        '''_funclist() --> get a list of strings containing all IDL functions'''
        tmp = 'p0o9i8u7y6'
        self.pyidl.eval(tmp+" = '"+tmp+"'")
        self.pyidl.eval(tmp+" = ROUTINE_NAMES(/S_FUNCTIONS)")
        #self.pyidl.eval(tmp+" = ROUTINE_NAMES(/FUNCTIONS, /UNRESOLVED)")
        self.pyidl.eval(tmp+" = STRJOIN("+tmp+", "+sep+")") 
        funclist = self.pyidl.getvar(tmp).split()
        self.delete(tmp)
        return funclist

    def _wholist(self):
        '''_wholist() --> get a list of strings containing all IDL variables'''
        #XXX: ROUTINE_NAMES is 'obsolete', a 'better' solution is:
        #    IDL> help, names='*', OUTPUT=p0o9i8u7y6
        #    IDL> p0o9i8u7y6 = STRJOIN(p0o9i8u7y6, STRING(10b))
        #    varlist = self.pyidl.getvar('p0o9i8u7y6').split()
        #    then crop out the varnames from the varlist...
        tmp = 'p0o9i8u7y6'
        self.pyidl.eval(tmp+" = '"+tmp+"'")
        self.pyidl.eval(tmp+" = ROUTINE_NAMES(variables=1)")
        self.pyidl.eval(tmp+" = STRJOIN("+tmp+", "+sep+")") 
        varlist = self.pyidl.getvar(tmp).split()
        varlist.remove(tmp.upper())
        self.delete(tmp)
        return varlist

    def _exists(self,name):
        '''_exists(name) --> True if is a variable in IDL'''
        exists = self._wholist().count(name.upper())
        if exists: return True
        return False

    def _isIDLfunc(self,name):
        '''_isIDLfunc(name) --> True if is an IDL function'''
        exists = self._funclist().count(name.upper())
        if exists: return True
        return False

    def _isIDLpro(self,name):
        '''_isIDLpro(name) --> True if is an IDL procedure'''
        exists = self._prolist().count(name.upper())
        if exists: return True
        return False

    def _isarrayobj(self,obj):
        '''_isarrayobj(obj) --> True if is an IDL_Array obj'''
        #FIXME: this is NOT a good way to check, but usually will work...
        if hasattr(obj,'name') and \
           hasattr(obj,'shape') and \
           hasattr(obj,'isize') and \
           hasattr(obj,'get') and \
           hasattr(obj,'set') and \
           hasattr(obj, 'type'): return True
        return False

    def _invertshape(self,shape):
        '''_invertshape(shape) --> translate shape between IDL and NumArray'''
        if not isinstance(shape,tuple):
            raise TypeError, "%r not a valid shape tuple" % shape
        shapelist = list(shape)
        shapelist.reverse()
        return tuple(shapelist)

    def _putstringarr(self,name,value):
        '''_putstringarr(name,value) --> put list of strings as STRING Array'''
        self._validate(name)
        if not isinstance(value,list):
            raise TypeError, "%r not converted to IDL STRING array" % str(name)
        strlist = []
        for i in range(len(value)):
            strlist.append(str(value[i]))
        self.pyidl.eval(name+" = STRARR("+str(len(strlist))+")")
        for i in range(len(strlist)):
            self.pyidl.eval(name+"["+str(i)+"] = '"+strlist[i]+"'")
       ####ALTERNATE IMPLEMENTATION###
       #strarray = []
       #for i in range(len(strlist)):
       #    strarray.append(numarray.array(strlist[i]))
       #strarray = numarray.array(strarray,type='Int8')
       #self.put(name,strarray,type='Int8') #FIXME: byte order is jumbled!!!
       #self.pyidl.eval(name+" = STRING(TRANSPOSE("+name+"))")
       ###############################
        self._putlocal(name,strlist)
        return

    def _processstringarrayobj(self,obj):
        '''_processstringarrayobj(obj) --> get IDL string array as a list'''
        if not self._isarrayobj(obj):
            raise TypeError, "object is not an IDL_array object"
        if obj.type() is not 7:
            raise TypeError, "'%s' is not an IDL STRING array" % str(obj.name())
        tmp = 'p0o9i8u7y6'
        self.pyidl.eval(tmp+" = '"+tmp+"'")
        self.pyidl.eval(tmp+" = STRJOIN("+obj.name()+", "+sep+")") 
        val = self.pyidl.getvar(tmp).split()
        self.delete(tmp)
        self._delarr(obj.name())
        self._putlocal(obj.name(),obj,store='getbuff')
        self._putstringarr(obj.name(),val)
        return val

    def _processobj(self,obj,array='?'):
        '''_processobj(obj,[array]) --> extract value from IDL_array obj'''
        if not self._isarrayobj(obj):
            raise TypeError, "object is not an IDL_array object"
        if obj.type() is 7: #is an IDL STRING Array
            return self._processstringarrayobj(obj)
        numtyp = self.types[obj.type()]
        numarrayshape = self._invertshape(obj.shape())
        val = numarray.array(buffer(obj),type=numtyp,shape=numarrayshape)
        if array == '?': #check what is stored locally
            array = self._toarray(obj.name())
        if not array:
            if val.typecode() is '1': #BYTE-type (unicode)
                val = val.tostring()
                array = True #this preserves the BYTE Array on call to _put
            elif not val.rank:  #convert rank-0 to rank-1
                val = numarray.array([val],type=numtyp).tolist()
                val = val[0] #convert back to rank-0
            else:               #rank-1 through n
                val = val.tolist()
        else: val = numarray.array(val,numtyp) #uncouple from buffer
        self.put(obj.name(),val,array,numtyp) #reset memory reference
        self._putlocal(obj.name(),obj,store='getbuff')
        self._putlocal(obj.name(),val)
        return val

    def _putvar(self,name,value,allowNone=False):
        '''_putvar(name,value) --> put a scalar into IDL'''
        self._validate(name)
        exists = self._exists(name)
        try: #Py_None creates IDL_TYP_UNDEF, but throws ValueError
            self.pyidl.setvar(name,value)
        except TypeError: #non-scalar creates IDL_TYP_UNDEF if new
            if not exists: self.delete(name)
            raise TypeError, "value '%s' is not an IDL scalar" % str(value)
        except ValueError:
            if not allowNone: #delete undefined variable; raise error
                if not exists: self.delete(name)
                raise
            if exists: #now allowNone should set to IDL_TYP_UNDEF
                self.delete(name)
                self._putvar(name,None,allowNone=True) #run again
        self._putlocal(name,value)
        return

    def _checkarray(self,name,value,array=None,type=None):
        '''_checkarray(name,value,[array,type]) --> set (array,type) for _put'''
        if array == None: #check if value is an array
            if hasattr(value,'type'): array = True #value is array, put array
            else: array = False #value not array, don't put array
        if array == '?': #check what is stored locally
            array = self._toarray(name)
        if not array: return False,None #non-arrays don't have types!
        if type == None and hasattr(value,'type'):
            type = value.type() #set type to value's type
        if type == '?': type = self._totype(name) #check local type
        return array,type

    def _delarr(self,name):
        '''_delarr(name) --> delete array from IDL'''
        obj1 = self._poplocal(name,store='getbuff')
        obj2 = self._poplocal(name,store='putbuff')
        if obj1 or obj2: self._poplocal(name)
        return

    def _synclocal(self,name=None):
        '''_synclocal([name]) --> update local store value to IDL value'''
        if name: varlist = [name]
        else: varlist = self._wholist()
        for varname in varlist: #update local store with IDL variable values
            vn = varname.strip()
            self.get(vn,allowNone=True)
        if not name:
            for key in self.whos.keys():
                if key not in varlist: #delete local not in IDL
                    self.delete(key)
        return

### 'PUBLIC' METHODS ###

    def delete(self,name):
        '''delete(name) --> destroy selected IDL variables'''
        self._validate(name)
        command = 'delvar, '+name
        self.pyidl.eval(command)
        self._delarr(name)
        self._poplocal(name)
        return

    def map(self,name=None):
        '''map([name]) --> get the IDL data type mapping'''
        if name: return self.types[name]
        return self.types

    def help(self,name=None):
        '''help([name]) --> print the IDL help message (for a variable)'''
        command = 'help'
        if name: command += ', '+name
        self.pyidl.eval(command)
        return

    def get(self,name,array='?',allowNone=False):
        '''get(name,[array,allowNone]) --> fetch a variable from IDL'''
        if self._isexpr(name): #contains 'expression' syntax
            return self._getexpr(name,array,allowNone)
        self._validate(name)
        if not self._exists(name):
            raise NameError, "'%s' is not defined in IDL" % str(name)
        if allowNone: #retrieve existing NoneTypes
            try: #IDL_TYP_UNDEF throws AttributeError
                value = self.pyidl.getvar(name)
            except AttributeError:
                value = None #should be NoneType, set value = None
        else: value = self.pyidl.getvar(name) #fail on None
        if self._isarrayobj(value):
            value = self._processobj(value,array) #extract array
        self._putlocal(name,value)
        return value

    def put(self,name,value,array=None,type=None,allowNone=False):
        '''put(name,value,[array,type,allowNone]) --> push a variable to IDL'''
        if self._isexpr(name): #contains 'expression' syntax
            return self._putexpr(name,value,array,type,allowNone)
        try: len(value)  #catch all non-sequence items 
        except TypeError: return self._putvar(name,value,allowNone)
        self._validate(name)
        array,type = self._checkarray(name,value,array,type)
        if not array and isinstance(value, str): #put as string, not BYTE Array
            return self._putvar(name,value,allowNone)
        try: z = numarray.array(value,type) #convert to temporary NumArray
        except TypeError: #raised when list contains non-numeric items
            return self._putstringarr(name,value)
        self._delarr(name)
        idlshape = self._invertshape(z._shape)
        obj = self.pyidl.setarr(name,z._data,self.types[z._type],idlshape)
        self._putlocal(name,obj,store='putbuff')
        self._putlocal(name,value)
        ### CORRECT THE VALUE IN LOCAL STORE BASED ON ARRAY & TYPE ###
        #return self._synclocal(name) #cannot be used due to infinite loop
        if not array and self._isarray(name): #convert from NumArray
            if z.typecode() is '1': #BYTE-type (unicode)
                value = z.tostring()
            else:                   #rank-1 through n
                value = z.tolist()
        elif array and not self._isarray(name): #convert to NumArray
            value = numarray.array(z,type)
        if array: #make sure converted to correct type
            value = numarray.array(value,type)
        self._putlocal(name,value)
        return

    def who(self,name=None,local=False,stdout=False):
        '''who([name,local,stdout]) --> print/return the IDL/local variables'''
        if not local:
            self._synclocal(name) #XXX:? Should I also sync if local=True ???
            if not stdout:
                return self.who(name,local=True,stdout=False)
            command = ''
            if name: command += 'print, '+name
            else:
                for varname in self.whos.keys():
                    vn = varname.strip()
                    command += "print, '"+vn+":' & print, "+vn+" & "
            self.pyidl.eval(command)
            return
        if name: vars = self._getlocal(name,skip=False)
        else: vars = self.whos
        if not stdout: return vars #then return the object
        print vars #otherwise, just print to stdout & return None
        return 

#   def _print(self,name):
#       '''_print(name) --> print using the IDL print command'''
#       self.who(name,stdout=True)
#       return

    #NOTE: to build NoneType... eval("A = A"), when 'A' does not exist.
    def eval(self,command): #NOTE: much of rsiidl code may use pyidl.eval???
        '''eval(command) --> execute an IDL command'''
        command = self._processIDLcommand(command)
        if not command: return #do nothing, is just a comment or NULL
        self._putevalbuff(command)
        idlcommand = self._processevalbuff()
        if not idlcommand: return #wait on next line
        self.pyidl.eval(idlcommand)
        self._synclocal() #XXX: time consuming?
       ####ALTERNATE IMPLEMENTATION###
       #split command using _splitIDLmultiple()
       #regex for '=', then sync LHS using _hasIDLassignment()
       #_hasIDLrange may be needed to catch subscripts
       ###############################
        return

    def prompt(self):
        '''an interactive IDL session'''
        #Access to python is given with the 'python()' command'''
        print "IDL interface:"
        self.help() #print current variables
        while 1:
            com = raw_input('IDL> ')
##          print com
            if com == 'exit': break
            self.eval(com)
        return #XXX: allow python commands?

    def doc(self):
        print self.__doc__
        print __license__[-391:] # print copyright and reference
        return

### END 'PUBLIC' METHODS ###

    def _processIDLcommand(self,command):
        '''_processIDLcommand(command) --> preprocess ';' and '$' in command'''
        import re
        #if begins with ';', then ignore whole line
        p_iscomment = re.compile('^\s*;')
        if p_iscomment.match(command): return
        #if begins with '$' and evalbuf is empty, then don't touch
        if command.lstrip(' ') != command.lstrip(' $') and not self.evalbuff:
            return command #is os command
        #if command not os command, delete all after ';'
        p_hascomment = re.compile(';')
        command = p_hascomment.split(command)[0]
        #if '$' and evalbuf is not empty, delete all after '$'
        #FIXME: '$' allowed in variable names { IDL> a$b = 1   }
        p_hascontinue = re.compile('\$')
        if command.count('$'):
            command = p_hascontinue.split(command)[0]+'$' #keep '$' as indicator
        #return processed command
        return command

    def _putevalbuff(self,command):
        '''_putevalbuff(command) --> add command to evalbuff'''
        return self.evalbuff.append(command)

    def _processevalbuff(self):
        '''_processevalbuff() --> prepare evalbuff as a single IDL command'''
        #don't launch when last line ends with '$'
        #FIXME: '$' allowed in variable names { IDL> x = ab$   }
        if not self.evalbuff: return
        if len(self.evalbuff) == 1 and self.evalbuff[0].strip(' ') == '$':
            self.evalbuff = []
            return '$' #command to begin os shell
        if self.evalbuff[-1].endswith('$'):
            self.evalbuff[-1] = self.evalbuff[-1].rstrip('$') #kill trailing '$'
            return
        command = ' '.join(self.evalbuff)
        self.evalbuff = []
        return command

    def _splitIDLmultiple(self,command): # '&'
        raise NotImplementedError
        return command.split('&')

    def _hasIDLassignment(self,command): # '=' & '?:'
        raise NotImplementedError

    def _hasIDLrange(self,command): # ':' & '*'
        raise NotImplementedError

    def _validateexpr(self,name,lhs=False):
        '''_validateexpr(name,[lhs]) --> raise if invalid expression'''
        #lhs=True for 'put', but lhs=False for 'get'
        #a valid IDL expression has an equal number of '[' and ']',
        #and includes a valid IDL expression within the '[]'
        #a valid IDL expression has an equal number of '(' and ')',
        #and includes a valid IDL expression within the '()'
        ##i.e. nesting must be correct...
        #a valid IDL lhs cannot have an operator more external than '[]',
        #unless '()' is used as parenthesis and not a function 
        return

    def _isexpr(self,expr):
        '''_isexpr(expr) --> True if includes valid form of IDL subexpression'''
        import re
        pattern = '[_a-zA-Z0-9]+\[[^\[\]]+?\]'
        newexpr = re.compile(pattern).sub('x',expr) #also '$'
        pattern = '[_a-zA-Z0-9]*\([^\(\)]*?\)'
        newexpr = re.compile(pattern).sub('x',newexpr) #ditto
        if newexpr != expr: return True
        return False

    def _exprroot(self,expr,allowUndefined=True):
        '''_exprroot(expression,[allowUndefined]) --> extract root variables'''
        #extracts the root(s) of an IDL expression...
        import re
        #remove all from operator1-operator3, except for '('
        expr = re.compile('[\*\^\+\-\#\/\<\>\&\|\~\?\:\,\)\[\]]').sub(' ',expr)
        #remove all digits not attached to a non-digit
        expr = re.compile('\s\d+[\s\d]*').sub('  ',expr)
        expr = re.compile('\A\d+[\s\d]*').sub('  ',expr)
        #remove all names prefixed to a '('
        expr = re.compile('\w*[\(]').sub(' ',expr)
        namelist = []
        for name in expr.split():
            try: #check if name is valid
                self._validate(name)
                namelist.append(name)
            except NameError:
                pass #skip any non-valid names
        if allowUndefined: return namelist
        varlist = self._wholist()
        defined = []    
        for var in namelist:
            if var.upper() in varlist: defined.append(var)
        return defined
        ### WEAKER ALTERNATE ###
        #XXX: this does not work for undefined variable names
        #namelist = []
        #for var in self.whos.keys():
        #    #XXX: first = [a-zA-Z]  #else = [_$a-zA-Z0-9]
        #    pmatch = re.compile('[^_$a-zA-Z0-9]'+var+'[^_a$a-zA-Z0-9]')
        #    match = pmatch.search(name)
        #    if match: namelist.append(match[1:-1]) #strip off 1st & last chars
        ########################

    def _sortexists(self,namelist):
        '''_sortexists(namelist) --> sort list into existing (and non-)'''
        if not isinstance(namelist,list):
            raise TypeError, "'%s' is not a list of names" % str(namelist)
        defined = []
        undefined = []
        for name in namelist:
            if self._exists(name): defined.append(name)
            else: undefined.append(name)
        return defined,undefined

    def _putexpr(self,name,value,array=None,type=None,allowNone=False):
        '''_putexpr(name,value,[array,type,allowNone]) --> set array portion'''
        ### BETTER IF THIS METHOD USES SOMETHING LIKE obj.setitem ? ###
        self._validateexpr(name)
        tmp = 'q1w2e3r4t5'
        rootlist = self._exprroot(name)
        rootlist,undefined = self._sortexists(rootlist)
        #varlist = self._wholist()
        try:
            self.put(tmp,value,array,type,allowNone)
            self.pyidl.eval(name+' = '+tmp)
        except: #AttributeError, NameError #FIXME
            #newvarlist = self._wholist()
            #for var in newvarlist:
            #    if var not in varlist: self.delete(var) #delete new variables
            for var in undefined: self.delete(var)
            self.delete(tmp)
            raise
        self.delete(tmp)
        for var in undefined: self.delete(var)
        for root in rootlist:
            self._synclocal(root)
        return

    def _getexpr(self,name,array='?',allowNone=False):
        '''_getexpr(name,[array,allowNone]) --> get array portion'''
        ### BETTER IF THIS METHOD USES SOMETHING LIKE ojb.getitem ? ###
        self._validateexpr(name)
        tmp = 'a1s2d3f4g5'
        rootlist = self._exprroot(name)
        rootlist,undefined = self._sortexists(rootlist)
        #varlist = self._wholist()
        try:
            self.pyidl.eval(tmp+' = '+name)
            value = self.get(tmp,array,allowNone)
        except: #AttributeError, NameError #FIXME
            #newvarlist = self._wholist()
            #for var in newvarlist:
            #    if var not in varlist: self.delete(var) #delete new variables
            for var in undefined: self.delete(var)
            self.delete(tmp)
            raise
        self.delete(tmp)
        return value
