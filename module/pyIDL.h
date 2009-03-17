#ifndef PYIDL_H
#define PYIDL_H

#ifndef PYTHON_INCLUDED
  #define PYTHON_INCLUDED
  #include "Python.h"
#endif

// API for IDL

extern char pyIDL_open__name__[];
extern char pyIDL_open__doc__[];
extern "C" PyObject *pyIDL_open(PyObject *, PyObject * args);

extern char pyIDL_close__name__[];
extern char pyIDL_close__doc__[];
extern "C" PyObject *pyIDL_close(PyObject *, PyObject * args);

extern char pyIDL_eval__name__[];
extern char pyIDL_eval__doc__[];
extern "C" PyObject *pyIDL_eval(PyObject *, PyObject * args);

extern char pyIDL_getvar__name__[];
extern char pyIDL_getvar__doc__[];
extern "C" PyObject *pyIDL_getvar(PyObject *, PyObject * args);

extern char pyIDL_setvar__name__[];
extern char pyIDL_setvar__doc__[];
extern "C" PyObject *pyIDL_setvar(PyObject *, PyObject * args);

extern char pyIDL_setarr__name__[];
extern char pyIDL_setarr__doc__[];
extern "C" PyObject *pyIDL_setarr(PyObject *, PyObject * args);

extern char pyIDL_getarr__name__[];
extern char pyIDL_getarr__doc__[];

extern char pyIDL_getmap__name__[];
extern char pyIDL_getmap__doc__[];
extern "C" PyObject *pyIDL_getmap(PyObject *, PyObject * args);


#endif

// version
// $Id$
// End of file
