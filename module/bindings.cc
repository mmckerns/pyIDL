#include "bindings.h"
#include <Python.h>
#include "pyIDL.h"       // Simple Api for IDL

// the method table
struct PyMethodDef pyIDL_methods[] = {
  {pyIDL_open__name__,pyIDL_open,METH_VARARGS,pyIDL_open__doc__},
  {pyIDL_close__name__,pyIDL_close,METH_VARARGS,pyIDL_close__doc__},
  {pyIDL_eval__name__,pyIDL_eval,METH_VARARGS,pyIDL_eval__doc__},
  {pyIDL_getvar__name__,pyIDL_getvar,METH_VARARGS,pyIDL_getvar__doc__},
  {pyIDL_setvar__name__,pyIDL_setvar,METH_VARARGS,pyIDL_setvar__doc__},
  {pyIDL_setarr__name__,pyIDL_setarr,METH_VARARGS,pyIDL_setarr__doc__},
  {pyIDL_getarr__name__,pyIDL_getvar,METH_VARARGS,pyIDL_getarr__doc__},
  {pyIDL_getmap__name__,pyIDL_getmap,METH_VARARGS,pyIDL_getmap__doc__},
  {0,0} /* sentinel */
//{NULL, NULL, 0, NULL} /* sentinel */
};

//version 
// $Id$
// End of file
