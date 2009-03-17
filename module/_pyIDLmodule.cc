#ifdef WIN32
#include "stdafx.h"
#endif

#include <Python.h>
//#include "exceptions.h"
#include "bindings.h"

// Initialization function for the module
char pyIDL_module__doc__[] = "Simple API for IDL\n";
extern "C"
#ifdef WIN32
__declspec(dllexport)
#endif
void init_pyIDL(void) {
  PyObject *var, *mod, *dict;
  // create the module and add the functions
  mod = Py_InitModule4("_pyIDL",pyIDL_methods,
                       pyIDL_module__doc__,0,PYTHON_API_VERSION);
  // get its dictionary
  dict = PyModule_GetDict(mod);
  // check for errors
  if (PyErr_Occurred()) {
    Py_FatalError("can't initialize module IDL");
  }
  // install the module exceptions
//pyIDL_runtimeError = PyErr_NewException("IDL.runtime",0,0);
//PyDict_SetItemString(dict,"RuntimeException",pyIDL_runtimeError);
  return;
}

// version
// $Id$
// End of file
