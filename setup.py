#!/usr/bin/env python
# 
# Michael McKerns
# mmckerns@caltech.edu 
from sys import platform
import os

###############################################################################
# these are defaults for common environment variables
# (if you are stuck, a good guide is in ${IDL_DIR}/bin/idl)
idl_release_current = '7.0'         #XXX: see ${IDL_DIR}/version.txt
idl_version = '706'                 #XXX: kludge for no symlinks on windows :)
###############################################################################
idl_dir_nux = '/usr/local/itt/idl'  #HINT: relnotes.html lives there
idl_incdir_nux = '/external/include' # HINT: idl_export.h lives there
idl_libdir_nux = '/bin/bin.linux.x86' # HINT: .../bin.$OS.$ARCH
x11_libdir_nux = '/usr/lib'         #HINT: libX11.so lives there
# Mac
idl_dir_mac = '/Applications/itt/idl' # or 'opt/local/itt/idl'
idl_incdir_mac = '/external/include'
idl_libdir_mac = '/bin/bin.darwin.i386'
x11_libdir_mac = '/usr/X11R6/lib'
# Windows
idl_dir_win = 'C:\Program Files\ITT\IDL'+idl_version #XXX: kludge for windows
idl_incdir_win = '\external\include'
idl_libdir_win = '\bin\bin.x86'
###############################################################################

# check if easy_install is available
try:
#   import __force_distutils__ #XXX: uncomment to force distutils to be used
    from setuptools import setup, Extension
    has_setuptools = True
except ImportError:
    from distutils.core import setup, Extension
    has_setuptools = False

# build the 'setup' call
setup_code = """
setup(name='pyIDL',
      version='0.7',
      description='Python bindings for ITT IDL',
      author = 'Mike McKerns',
      author_email = 'mmckerns@caltech.edu',
      url = 'http://www.its.caltech.edu/~mmckerns/software.html',
      packages=['pyIDL'],
      package_dir={'pyIDL':''},
      ext_modules=[module1],
"""

# add dependencies
x11_version = '>=6.0'
idl_version = '>=6.0'
numarray_version = '>=1.5.2'
if has_setuptools:
    setup_code += """
      install_requires=("numarray%s"),
      dependency_links = ["http://dev.danse.us/packages/"],
""" % numarray_version

# close 'setup' call
setup_code += """    
      )
"""

#check if environment variables were set...
try:
    idl_release = os.environ['IDL_VERSION']
    idl_release_found = True
except KeyError:
    idl_release = idl_release_current
    idl_release_found = False
   #raise "set enviroment variable 'IDL_VERSION' to the idl version number"

try:
    idl_dir = os.environ['IDL_DIR']
    idl_dir_found = True
except KeyError:
    idl_dir_found = False
   #raise "set enviroment variable 'IDL_DIR' to the idl install directory"

try:
    idl_incdir = os.environ['IDL_INCDIR']
    idl_incdir_found = True
except KeyError:
    idl_incdir_found = False
   #raise "set enviroment variable 'IDL_INCDIR' to idl's include directory"

try:
    idl_libdir = os.environ['IDL_BINDIR']
    idl_libdir_found = True
except KeyError:
    idl_libdir_found = False
   #raise "set enviroment variable 'IDL_BINDIR' to idl's binary lib directory"


#build the extension module
if platform[:3] == 'win':
    myOS = 'win'
    # if stuff is missing, try the defaults...
    if not idl_dir_found:
        idl_dir = idl_dir_win
    if not idl_libdir_found:
        idl_libdir = idl_dir + idl_libdir_win
    if not idl_incdir_found:
        idl_incdir = idl_dir + idl_incdir_win

    if float(idl_release) >= float('7.0'):
        IDLLIBS = ['idl'] #XXX: more?  see ${IDL_DIR}\external\callable\makefile
    else: #?.? to 6.?
        IDLLIBS = ['idl32']

    module1 = Extension('_pyIDL',
                       ['module\\bindings.cc',
                        'module\_pyIDLmodule.cc',
                        'module\pyIDL.cc'],
                       include_dirs=['module', idl_incdir],
                       libraries=IDLLIBS,
                       library_dirs=[idl_libdir],
                       )
else: #platform = linux or mac
    try:
        x11_libdir = os.environ['X11_LIBDIR']
        x11_libdir_found = True
    except KeyError:
        x11_libdir_found = False
       #raise "set enviroment variable 'X11_LIBDIR' to X11's library directory"

    if float(idl_release) >= float('6.3'):
        IDLLIBS = ['idl','Xm','Xp','Xpm','Xmu','Xext','Xt','SM','ICE',
                   'Xinerama','X11','dl','termcap','rt','m','pthread','gcc_s'] 
    else: #6.0 to 6.2
        IDLLIBS = ['idl','Xm','Xp','Xpm','Xext','Xt','SM','ICE','X11',
                   'dl','termcap','rt','m','pthread'] 

    if platform[:6] == 'darwin':
        myOS = 'mac'
        IDLLIBS.remove('rt')
        IDLLIBS.remove('gcc_s') 
       #######################################################################
       #XXX: the following are not required in 7.0, when linking to IDL's X11
       #IDLLIBS.remove('Xinerama')
       #IDLLIBS.remove('Xpm')
       #IDLLIBS.remove('Xmu')
       #IDLLIBS.remove('Xext')
       #IDLLIBS.remove('Xp')
       #IDLLIBS.remove('Xt')
       #IDLLIBS.remove('X11')
       #######################################################################
        IDLLIBS.append('MesaGL6_2')
        IDLLIBS.append('MesaGLU6_2')
        IDLLIBS.append('OSMesa6_2')
        if float(idl_release) >= float('7.0'):
            IDLLIBS.append('freetype2_3_6')
        else: # 6.? to 6.4
            IDLLIBS.append('freetype2_1_3') 

    # if stuff is missing, try the defaults...
        if not idl_dir_found:
            idl_dir = idl_dir_mac
        if not idl_libdir_found:
            idl_libdir = idl_dir + idl_libdir_mac
        if not idl_incdir_found:
            idl_incdir = idl_dir + idl_incdir_mac
        if not x11_libdir_found:
            x11_libdir = x11_libdir_mac
    else:
        myOS = 'nux'
        if not idl_dir_found:
            idl_dir = idl_dir_nux
        if not idl_libdir_found:
            idl_libdir = idl_dir + idl_libdir_nux
        if not idl_incdir_found:
            idl_incdir = idl_dir + idl_incdir_nux
        if not x11_libdir_found:
            x11_libdir = x11_libdir_nux


    module1 = Extension('_pyIDLmodule',
                       ['module/bindings.cc',
                        'module/_pyIDLmodule.cc',
                        'module/pyIDL.cc'],
                       include_dirs=['module', idl_incdir],
                       libraries=IDLLIBS,
                       library_dirs=[x11_libdir, idl_libdir],
                       )

# exec the 'setup' code
exec setup_code

# if dependencies are missing, print a warning
try:
    import numarray
    from os import system
    if myOS != 'win':
        idl_missing = system("which idl") #FIXME: doesn't work on windows
        if idl_missing: raise ImportError
    #FIXME: add a check for X11
except ImportError:
    print "\n***********************************************************"
    print "WARNING: One of the following dependencies is unresolved:"
    print "    Numarray %s" % numarray_version
    print "    IDL %s" % idl_version
    if myOS != 'win':
        print "    X11 %s" % x11_version
    print "***********************************************************\n"

# code will fail if LD_LIBRARY_PATH & PATH are not set
if myOS == 'mac':
    ldlibpath_type = 'DYLD_LIBRARY_PATH'
else: #XXX: linux for sure... don't remember about windows
    ldlibpath_type = 'LD_LIBRARY_PATH'

try:
    ldlibpath = os.environ[ldlibpath_type]
    if idl_libdir in ldlibpath.split(':'): pass
    else: raise KeyError
    mypath = os.environ['PATH']
    if idl_libdir in mypath.split(':'): pass
    else: raise KeyError
except KeyError:
    print "\n***********************************************************"
    print "WARNING: idl executable and shared libraries cannot be found:"
    print "    Append %s" % idl_libdir
    print "    to your PATH and %s" % ldlibpath_type
    print "***********************************************************\n"

# print report on which paths were used
if idl_release_found and idl_dir_found and \
   idl_libdir_found and idl_incdir_found and x11_libdir_found:
    pass
else:
    print "\n***********************************************************"
    print "WARNING: One of following variables was set to a default:"
    print "    IDL_VERSION %s" % idl_release
    print "    IDL_DIR %s" % idl_dir
    print "    IDL_INCDIR %s" % idl_incdir
    print "    IDL_BINDIR %s" % idl_libdir
    if myOS != 'win':
        print "    X11_LIBDIR %s" % x11_libdir
    print "***********************************************************\n"


# end of file
