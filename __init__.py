#!/usr/bin/env python
# 
# Michael McKerns
# mmckerns@caltech.edu 
from rsiidl import __doc__ as idldoc
__doc__ = idldoc

def idl(stdout=True):
    """idl([stdout]): get help with 'help(pyIDL)'"""
    from rsiidl import idl as idlFactory
    return idlFactory(stdout)

def copyright():
    from rsiidl import __license__
    return __license__
   #return "pyIDL module: Copyright (c) 2005-2009 Michael McKerns";

# tested against:  idl_x, x=[6.0, 6.2, 6.3, 6.4, 7.0]


#  End of file 
