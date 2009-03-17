print '''build python list'''
print '''>>> from numarray import *
>>> from numarray import NewAxis
>>> x = pi*arange(21)/10.
>>> y = cos(x)'''
from numarray import *
from numarray import NewAxis
x = pi*arange(21)/10.
y = cos(x)

print '''build a numarray matrix'''
print '''>>> xm = x[:,NewAxis]
>>> ym = y[NewAxis,:]
>>> m = (sin(xm) + 0.1*xm) - ym**2'''
xm = x[:,NewAxis]
ym = y[NewAxis,:]
m = (sin(xm) + 0.1*xm) - ym**2

print '''instantiate the IDL class'''
print '''>>> from pyIDL import idl
>>> ri = idl()'''
from pyIDL import idl
ri = idl()

#get help
#>>> ri.doc()

print '''create a colormap directly from python
>>> ri.image_cont(-2*m)'''
ri.image_cont(-2*m)
raw_input("Press 'Return' to continue...")

print '''create a colormap directly within IDL'''
print '''>>> ri.m = m
>>> ri('image_cont, m')'''
ri.m = m
ri('image_cont, m')  #use 'tv' instead?
raw_input("Press 'Return' to continue...")

print '''create a surface plot from within IDL'''
print '''>>> ri('surface, m')'''
ri('surface, m')
raw_input("Press 'Return' to continue...")

print '''delete a variable within IDL'''
print '''>>> ri.delete('m')'''
ri.delete('m')

print '''create a lineplot directly from python
>>> ri.plot(x,cos(x))'''
ri.plot(x,cos(x))
raw_input("Press 'Return' to continue...")

print '''create a lineplot directly within IDL'''
print '''>>> ri.x = x
>>> ri('plot, x, sin(x)')'''
ri.x = x
ri('plot, x, sin(x)')
raw_input("Press 'Return' to continue...")

print '''create a formatted lineplot from within IDL'''
print '''>>> ri.y = cos(x)
>>> ri("plot, x, y, thick=2, linestyle=5")'''
ri.y = cos(x)
ri("plot, x, y, thick=2, linestyle=5")
#NOTE: IDL doesn't handle color & symsize correctly on linux?
#ri("plot, x, y, color=green, symsize=large")
raw_input("Press 'Return' to continue...")

print '''create a formatted lineplot directly from python'''
print '''>>> ri.plot(x,-y,linestyle=3)'''
ri.plot(x,-y,linestyle=3)
raw_input("Press 'Return' to continue...")

print '''create a histogram using the IDL session interface'''
print '''#   TYPE THE FOLLOWING IN THE PROMPT:
#   IDL> bar_plot, histogram(y,binsize=0.1), title="foobar"
#   IDL> exit'''
print '''>>> ri.prompt()'''
ri.prompt()

print '''inspect variables within IDL'''
print '''>>> ri.who().keys()'''
print ri.who().keys()
print '''>>> ri.who('x')'''
print ri.who('x')

print '''get variables from IDL into python'''
print '''>>> ri.y'''
print ri.y
print '''>>> ri.y[0]'''
print ri.y[0]
