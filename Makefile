CC	= g++
CFLAGS	= -fpic -I$(PYTHON_INCDIR) -I$(IDL_INCDIR)
LDFLAGS = -shared $(CFLAGS)
#X11_DIR = /usr
X11_DIR = ${HOME}
LIBS	= -L$(IDL_BINDIR) -lidl -Wl,-rpath,. -Wl,-rpath $(IDL_BINDIR)\
	-lXp -L${X11_DIR}/lib -lXm -lXpm -lXext -lXt -lSM -lICE -lX11 \
	-ldl -ltermcap -lrt -lm -lpthread -lXinerama -lXmu -lgcc_s
#---------------------------------------------------
SOURCES	= module/pyIDL.cc module/bindings.cc module/_pyIDLmodule.cc
OBJECTS	= pyIDL.o bindings.o _pyIDLmodule.o
#---------------------------------------------------

all: base wrap

base:
	$(CC) $(CFLAGS) -c $(SOURCES)

wrap: base
	$(CC) $(LDFLAGS) -o _pyIDL.so $(OBJECTS) $(LIBS)

clean:
	rm -f a.out core *.o

restore: clean
	rm -f *.pyc _*.so 
