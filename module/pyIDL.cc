// -*- CXX -*-
//
/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 * pyIDL.cc
 *
 * 10/12/2004 version 0.0.1b
 * mmckerns@caltech.edu & tkelley@caltech.edu
 * (C) 2004 All Rights Reserved
 *
 * <LicenseText>
 *
 * (Python-IDL is Copyright (c) 2002 Andrew McMurry; All Rights Reserved)
 * Andrew McMurry's Python-IDL was modified to include some of the
 * functionallity of the DANSE saidl module, specifically:
 *  - support for MSWindows
 *  - conversion between IDL arrays and numarray arrays
 *  - conversion between IDL arrays and StdVector objects (TODO)
 *  - however, some of the array methods were cut
 *~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 */

#include "pyIDL.h"
#include <Python.h>
#include "idl_export.h"
#include <string>
#include <iostream>

#ifdef WIN32
  #include <Windows.h>
#endif

#if (PY_VERSION_HEX < 0x02050000)
  typedef int Py_ssize_t;
  #define lenfunc inquiry
  #define readbufferproc getreadbufferproc
  #define writebufferproc getwritebufferproc
  #define segcountproc getsegcountproc
  #define charbufferproc getcharbufferproc
  #define ssizeargfunc intargfunc
  #define ssizessizeargfunc intintargfunc
  #define ssizeobjargproc intobjargproc
  #define ssizessizeobjargproc intintobjargproc
#endif 


using std::string;
using std::cout;
using std::endl;

// casting IDL variables to PyC
static PyObject *v_idl_2_py(void *value, UCHAR type) {
  Py_complex c;
  switch (type) {
  case IDL_TYP_BYTE:
    return Py_BuildValue("b", *(unsigned char *)value);
  case IDL_TYP_INT:
    return Py_BuildValue("h", *(short *)value);
  case IDL_TYP_UINT:
    return Py_BuildValue("i", (int)*(unsigned short *)value);
  case IDL_TYP_LONG:
    return Py_BuildValue("i", *(IDL_LONG *)value);
  case IDL_TYP_ULONG:
    return Py_BuildValue("l", (long)*(IDL_ULONG *)value);
  case IDL_TYP_LONG64:
    return Py_BuildValue("l", (long)*(IDL_LONG64 *)value);
  case IDL_TYP_ULONG64:
    return Py_BuildValue("l", (long)*(IDL_ULONG64 *)value);
  case IDL_TYP_FLOAT:
    return Py_BuildValue("f", *(float *)value);
  case IDL_TYP_DOUBLE:
    return Py_BuildValue("d", *(double *)value);
  case IDL_TYP_COMPLEX:
    c.real = ((float *)value)[0];
    c.imag = ((float *)value)[1];
    return Py_BuildValue("D", &c);
  case IDL_TYP_DCOMPLEX:
    c.real = ((double *)value)[0];
    c.imag = ((double *)value)[1];
    return Py_BuildValue("D", &c);
  case IDL_TYP_STRING:
    return Py_BuildValue("s", IDL_STRING_STR((IDL_STRING *)value));
  default:
    break;
  }
  return NULL;
}

//////////////////// start Array stuff ////////////////////
// build idl_ArrayObject
typedef struct {
  PyObject_HEAD
  IDL_ARRAY *arr;
  UCHAR type;
  char *name;
  PyObject *buf;
} idl_ArrayObject;

// map IDL and PyC types via dictionary
static int set_idl_type(PyObject *map, PyObject *numarray,
			char *naname, int idlnum) {
  PyObject *ntype, *itype;
  ntype = PyObject_GetAttrString(numarray, naname);
  if (ntype == NULL) return 1;
  itype = PyInt_FromLong(idlnum);
  if (itype == NULL) return 1;
  if (PyDict_SetItem(map, ntype, itype) == -1) return 1;
  if (PyDict_SetItem(map, itype, ntype) == -1) return 1;
  Py_DECREF(ntype);
  Py_DECREF(itype);
  return 0;
}

// fetch IDL/numarray types dictionary
char pyIDL_getmap__name__[] = "getmap";
char pyIDL_getmap__doc__[] = "getmap(numarray) --> get IDL/numarray map";
PyObject *pyIDL_getmap(PyObject *self, PyObject *args) {
  PyObject *map, *numarray;
  if (!PyArg_ParseTuple(args, "O", &numarray)) return NULL;
  map = PyDict_New();
  if (map == NULL) return NULL;
//if (set_idl_type(map,numarray,"UInt8",IDL_TYP_BYTE)) return NULL;
  if (set_idl_type(map,numarray,"Int8",IDL_TYP_BYTE)) return NULL;
  if (set_idl_type(map,numarray,"Int16",IDL_TYP_INT)) return NULL;
  if (set_idl_type(map,numarray,"Int32",IDL_TYP_LONG)) return NULL;
  if (set_idl_type(map,numarray,"Float32",IDL_TYP_FLOAT)) return NULL;
  if (set_idl_type(map,numarray,"Float64",IDL_TYP_DOUBLE)) return NULL;
  if (set_idl_type(map,numarray,"Complex64",IDL_TYP_COMPLEX)) return NULL;
//if (set_idl_type(map,numarray,"Complex128",IDL_TYP_DCOMPLEX)) return NULL;
  if (set_idl_type(map,numarray,"UInt16",IDL_TYP_UINT)) return NULL;
  if (set_idl_type(map,numarray,"UInt32",IDL_TYP_ULONG)) return NULL;
  if (set_idl_type(map,numarray,"Int64",IDL_TYP_LONG64)) return NULL;
  if (set_idl_type(map,numarray,"UInt64",IDL_TYP_ULONG64)) return NULL;
  return map;
}

// get the IDL array name
static PyObject *idl_array_name(PyObject *self, PyObject *args) {
  idl_ArrayObject *arr = (idl_ArrayObject *) self;
  if (!PyArg_ParseTuple(args, "")) return NULL;
  if (arr->name != NULL)
    return Py_BuildValue("s", arr->name);
  Py_INCREF(Py_None);
  return Py_None;
}

// get the IDL array type
static PyObject *idl_array_type(PyObject *self, PyObject *args) {
  idl_ArrayObject *arr = (idl_ArrayObject *) self;
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return Py_BuildValue("i", (int)arr->type);
}

// get the IDL array shape
static PyObject *idl_array_shape(PyObject *self, PyObject *args) {
  idl_ArrayObject *arr = (idl_ArrayObject *) self;
  PyObject *t;
  int i;
  if (!PyArg_ParseTuple(args, "")) return NULL;
  t = PyTuple_New(arr->arr->n_dim);
  for (i=0; i<arr->arr->n_dim; i++)
    PyTuple_SET_ITEM(t, i, PyInt_FromLong(arr->arr->dim[i]));
  return t;
}

// get the size of an IDL array item (i.e. how large is the size on disk?)
static PyObject *idl_array_isize(PyObject *self, PyObject *args) {
  idl_ArrayObject *arr = (idl_ArrayObject *) self;
  if (!PyArg_ParseTuple(args, "")) return NULL;
  return Py_BuildValue("i", arr->arr->elt_len);
}

// get item from IDL array (i.e. if b = [1,2,3], get b[0])
static PyObject *idl_array_get(PyObject *self, PyObject *args) {
  idl_ArrayObject *arr = (idl_ArrayObject *) self;
  PyObject *o;
  int i;
  if (!PyArg_ParseTuple(args, "i", &i)) return NULL;
  if (i < 0 || i >= arr->arr->n_elts) {
    PyErr_Format(PyExc_IndexError, "IDL array index out of bounds");
    return NULL;
  }
  o = v_idl_2_py(arr->arr->data + arr->arr->elt_len * i, arr->type);
  if (o == NULL) {
    PyErr_Format(PyExc_TypeError, "IDL array has unconvertable type");
  }
  return o;
}

// set item in IDL array
static PyObject *idl_array_set(PyObject *self, PyObject *args) {
  idl_ArrayObject *arr = (idl_ArrayObject *) self;
  PyObject *o;
  void *ptr;
  int i;
  if (!PyArg_ParseTuple(args, "iO", &i, &o)) return NULL;
  if (i < 0 || i >= arr->arr->n_elts) {
    PyErr_Format(PyExc_IndexError, "IDL array index out of bounds");
    return NULL;
  }
  ptr = arr->arr->data + arr->arr->elt_len * i;
  /* here we need to coerce a Python value to an IDL one of a specific type! */
  /* perhaps we should use PyNumber_Int and PyNumber_Float */
  switch (arr->type) {
  case IDL_TYP_BYTE:
    if (PyInt_Check(o)) {
      if (PyInt_AS_LONG(o) < -128 || PyInt_AS_LONG(o) > 255) {
        PyErr_Format(PyExc_ValueError, "Integer to be stored as byte too big");
        return NULL;
      }
      *(char *)ptr = PyInt_AS_LONG(o);
    } else if (PyString_Check(o)) {
      if (PyString_GET_SIZE(o) != 1) {
        PyErr_Format(PyExc_ValueError,
                     "String of length != 1 to be stored as byte");
        return NULL;
      }
      *(char *)ptr = *PyString_AS_STRING(o);
    } else {
      PyErr_Format(PyExc_TypeError, "Bad type to store as a byte");
      return NULL;
    }
    break;
  case IDL_TYP_INT:
  case IDL_TYP_UINT:
    if (PyInt_Check(o)) {
      if (PyInt_AS_LONG(o) < -32768 || PyInt_AS_LONG(o) > 65535) {
        PyErr_Format(PyExc_ValueError,
                     "Integer to be stored as IDL int too big");
        return NULL;
      }
      *(short *)ptr = PyInt_AS_LONG(o);
    } else {
      PyErr_Format(PyExc_TypeError, "Bad type to store as an IDL int");
      return NULL;
    }
    break;
  case IDL_TYP_LONG:
  case IDL_TYP_ULONG:
    if (PyInt_Check(o)) {
      *(IDL_LONG *)ptr = PyInt_AS_LONG(o);
    } else {
      PyErr_Format(PyExc_TypeError, "Bad type to store as an IDL long");
      return NULL;
    }
    break;
  case IDL_TYP_LONG64:
  case IDL_TYP_ULONG64:
    if (PyInt_Check(o)) {
      *(IDL_LONG64 *)ptr = PyInt_AS_LONG(o);
    } else {
      PyErr_Format(PyExc_TypeError, "Bad type to store as an IDL long64");
      return NULL;
    }
    break;
  case IDL_TYP_FLOAT:
    if (PyFloat_Check(o)) {
      *(float *)ptr = PyFloat_AS_DOUBLE(o);
    } else {
      PyErr_Format(PyExc_TypeError, "Bad type to store as an IDL float");
      return NULL;
    }
    break;
  case IDL_TYP_DOUBLE:
    if (PyFloat_Check(o)) {
      *(double *)ptr = PyFloat_AS_DOUBLE(o);
    } else {
      PyErr_Format(PyExc_TypeError, "Bad type to store as an IDL double");
      return NULL;
    }
    break;
  default:
    PyErr_Format(PyExc_TypeError,
                 "IDL type currently unrecognised for setting");
    return NULL;
  }
  Py_INCREF(Py_None);
  return Py_None;
}

// IDL array methods
static PyMethodDef idl_array_methods[] = {
  {"isize", (PyCFunction)idl_array_isize, METH_VARARGS,
   "Return the item size."},
  {"shape", (PyCFunction)idl_array_shape, METH_VARARGS,
   "Return the shape."},
  {"get", (PyCFunction)idl_array_get, METH_VARARGS,
   "Get an item."},
  {"set", (PyCFunction)idl_array_set, METH_VARARGS,
   "Set an item."},
  {"name", (PyCFunction)idl_array_name, METH_VARARGS,
   "Return the variable name."},
  {"type", (PyCFunction)idl_array_type, METH_VARARGS,
   "Return the IDL type of the array elements."},
  {NULL, NULL, 0, NULL} // sentinel //
};

// get the IDL array attributes
static PyObject *idl_array_getattr(PyObject *self, char *name) {
  return Py_FindMethod(idl_array_methods, self, name);
}

// get array data buffer
static int idl_array_getbuf(idl_ArrayObject *self, int idx, void **pp) {
  if ( idx != 0 ) {
    PyErr_SetString(PyExc_TypeError, "IDL objects only support one segment");
    return -1;
  }
  *pp = self->arr->data;
  return self->arr->arr_len;
}

// get array segcount
static int idl_array_getsegcount(idl_ArrayObject *self, int *lenp) {
  if ( lenp )
    *lenp = self->arr->arr_len;
  return 1;
}

// IDL array buffer procedures
static PyBufferProcs idl_array_as_buffer = {
  (readbufferproc) idl_array_getbuf,
  (writebufferproc) idl_array_getbuf,
  (segcountproc) idl_array_getsegcount,
  (charbufferproc) idl_array_getbuf
};

// deallocate IDL array
static void idl_array_dealloc(PyObject *self) {
  idl_ArrayObject *arr = (idl_ArrayObject *) self;
  char buf[128];
  sprintf(buf, "delvar, %s", arr->name);
  IDL_ExecuteStr(buf);
  free(arr->name);
  Py_XDECREF(arr->buf);
  PyObject_Del(self);
}

// IDL array type object
static PyTypeObject idl_ArrayType = {
  PyObject_HEAD_INIT(NULL)
  0,
  "_IdlArray",
  sizeof(idl_ArrayObject),
  0,
  idl_array_dealloc,
  0,
  idl_array_getattr,
  0,
  0,
  0,
  // std classes //
  0,
  0,
  0,
  // more std opts //
  0,
  0,
  0,
  0,
  0,
  &idl_array_as_buffer,
  0,
  "Internal object for accessing an IDL array."
};

// get a named IDL array
char pyIDL_getarr__name__[] = "getarr";
char pyIDL_getarr__doc__[] = "getarr(name) --> get IDL Array";
static PyObject *idl_getarr(char *name) {
  idl_ArrayObject *arr;
  IDL_VPTR var;
  var = IDL_FindNamedVariable(name, FALSE); //FALSE == don't create
  arr = PyObject_New(idl_ArrayObject, &idl_ArrayType);
  arr->name = (char *) malloc(strlen(name)+1);
  strcpy(arr->name, name);
  arr->arr = var->value.arr;
  arr->type = var->type;
  arr->buf = NULL; 
  return (PyObject *) arr;
}

// free callback (when imported memory is released)
static void free_cb(UCHAR *buf) {
}

// set IDL array
char pyIDL_setarr__name__[] = "setarr";
char pyIDL_setarr__doc__[] = "setarr(name,data,type,shape) --> set IDL Array";
PyObject *pyIDL_setarr(PyObject *self, PyObject *args) {
  PyObject *buf, *shape, *n;
  idl_ArrayObject *arr;
  IDL_VPTR var;
  char *data, *name;
#if PY_VERSION_HEX >= 0x2050000 //XXX: or 020500F0 ???
  ssize_t len;
#else
  int len;
#endif
  int type, nd, i;
  IDL_MEMINT *dim;
  if (!PyArg_ParseTuple(args, "sOiO", &name, &buf, &type, &shape)) return NULL;
  if (PyObject_AsWriteBuffer(buf, (void **)(&data), &len) == -1) return NULL;
  nd = PyTuple_GET_SIZE(shape);
  dim = (IDL_MEMINT *) malloc(nd * sizeof(IDL_MEMINT));
  for (i = 0; i < nd; i++) {
    n = PyNumber_Int(PyTuple_GET_ITEM(shape, i));
    if (n == NULL) return NULL;
    dim[i] = PyInt_AsLong(n);
    Py_DECREF(n);
  }
  var = IDL_ImportNamedArray(name, nd, dim, type, (UCHAR *)data,
			     free_cb, NULL);
//			     0, 0); //don't use no callback
// create and return idl_ArrayObject
//arr = idl_getarr(name); //MMM FIXME???
  arr = PyObject_New(idl_ArrayObject, &idl_ArrayType);
  arr->name = (char *) malloc(strlen(name)+1);
  strcpy(arr->name, name);
  arr->arr = var->value.arr;
  arr->type = var->type;
  arr->buf = buf;
  Py_INCREF(arr->buf);
  return (PyObject *) arr;
/*Py_INCREF(Py_None);
  return Py_None; */
}
//////////////////// end Array stuff ////////////////////

// evaluate an IDL command string
char pyIDL_eval__name__[] = "eval";
char pyIDL_eval__doc__[] = "eval(command) --> execute IDL command";
PyObject *pyIDL_eval(PyObject *, PyObject * args) {
  char *command = 0;
  if (!PyArg_ParseTuple(args, "s", &command)) return NULL;
  IDL_ExecuteStr(command);
  Py_INCREF(Py_None);
  return Py_None;
}

// fetch a variable from IDL
char pyIDL_getvar__name__[] = "getvar";
char pyIDL_getvar__doc__[] = "getvar(name) --> fetch IDL variable";
PyObject *pyIDL_getvar(PyObject *self, PyObject *args) {
  char *name;
  IDL_VPTR var;
  PyObject *o;
  if (!PyArg_ParseTuple(args, "s", &name)) return NULL;
  var = IDL_FindNamedVariable(name, FALSE); //FALSE == don't create
  if (var == NULL || var->type == IDL_TYP_UNDEF) {
    PyErr_Format(PyExc_AttributeError,
		 "IDL variable undefined '%s'", name);
    return NULL;
  }
  if ((var->flags & (IDL_V_ARR | IDL_V_STRUCT | IDL_V_FILE)) == 0) {
    o = v_idl_2_py(&var->value, var->type);
    if (o) return o;
  } else if (var->flags & IDL_V_ARR) return idl_getarr(name); //MMM (see below)
/*} else if (var->flags & IDL_V_ARR) {
    PyErr_Format(PyExc_TypeError,
		 "IDL variable is not scalar '%s'", name);
    return NULL;
  }*/ 
  PyErr_Format(PyExc_TypeError,
	       "IDL variable has unconvertable type '%s'", name);
  return NULL;
}

// set a (scalar) variable in IDL
char pyIDL_setvar__name__[] = "setvar";
char pyIDL_setvar__doc__[] = "setvar(name,val) --> set IDL variable";
PyObject *pyIDL_setvar(PyObject *self, PyObject *args) {
  char *name;
  PyObject *v;
  IDL_VPTR var;
  IDL_ALLTYPES iv;
  if (!PyArg_ParseTuple(args, "sO", &name, &v)) return NULL;
  var = IDL_FindNamedVariable(name, TRUE); //TRUE = create if DNE
  if (var->flags & IDL_V_CONST) {
    PyErr_Format(PyExc_AttributeError,
		 "IDL variable is a constant '%s'", name);
    return NULL;
  }
  if (PyInt_Check(v)) {
    iv.l = PyInt_AS_LONG(v);
    IDL_StoreScalar(var, IDL_TYP_LONG, &iv);
  } else if (PyFloat_Check(v)) {
    iv.d = PyFloat_AS_DOUBLE(v);
    IDL_StoreScalar(var, IDL_TYP_DOUBLE, &iv);
  } else if (PyComplex_Check(v)) {
    iv.dcmp.r = PyComplex_RealAsDouble(v);
    iv.dcmp.i = PyComplex_ImagAsDouble(v);
    IDL_StoreScalar(var, IDL_TYP_DCOMPLEX, &iv);
  } else if (PyString_Check(v)) {
    IDL_StrStore(&iv.str, PyString_AS_STRING(v));
    IDL_StoreScalar(var, IDL_TYP_STRING, &iv);
  } else if (v == Py_None) {
    PyErr_Format(PyExc_ValueError,
		 "NoneType not converted to UNDEFINED IDL value");
    return NULL;
  } else {
    PyErr_Format(PyExc_TypeError,
		 "Value cannot be converted to an IDL value");
    return NULL;
  }
  Py_INCREF(Py_None);
  return Py_None;
}

// write IDL output to std::cout
static void IDLstdout(int flags, char *buff, int n) {
  string message(buff,n);
  cout<<message<<endl;
  return;
}

// swallow IDL output
static void IDLstdout0(int flags, char *buff, int n) {
  return;
}

// open IDL session
char pyIDL_open__name__[] = "open";
char pyIDL_open__doc__[] = "open() --> open IDL session";
int argc = 0; //MMM-XXX: no commandline args allowed
//int argc = 1; //MMM-XXX: commandline args allowed
char *argv[1] = { NULL };
//idl_ArrayType.ob_type = &PyType_Type;  //MMM
PyObject *pyIDL_open(PyObject *, PyObject * args) {
  int printme;
  if (!PyArg_ParseTuple(args, "i", &printme)) printme = 1;
#ifdef WIN32
  // Get HINSTANCE value for this module
  HMODULE our_hinst = GetModuleHandle("pyIDL");
  HWND our_hwnd = HWND();
  cout<<"Module instance handle is "<<our_hinst
      <<"; hwnd handle is "<<our_hwnd<<"."<<endl;
  // initialize IDL interpreter
  if(IDL_Win32Init(0, our_hinst, our_hwnd, 0)) {
#else
  // initialize IDL interpreter
  if(IDL_Init(0, &argc, argv)) {
//if(IDL_Init(0, 0, 0)) { //MMM
#endif
    // set output function:
    if(printme == 0) { //if call was open(0), then use no-stdout mode
      IDL_ToutPush(IDLstdout0);
    } else {
      IDL_ToutPush(IDLstdout);
    }
  } else {
    PyErr_SetString(PyExc_RuntimeError, 
                    "pyIDL_open: Unable to initialize IDL!");
    return 0;
  }
  Py_INCREF(Py_None);
  return Py_None;
}

// close IDL session
char pyIDL_close__name__[] = "close";
char pyIDL_close__doc__[] = "close() --> close IDL session";
PyObject *pyIDL_close(PyObject *, PyObject * args) {
    IDL_Cleanup(IDL_FALSE);
    Py_INCREF(Py_None);
    return Py_None;
}

