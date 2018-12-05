
include ../../build/flags.mk

INC = -I../../comun -I../../comun/utils
CXXFLAGS = $(GFLAGS) -MMD -MP $(INC) -O2

objs = voice_g711.o

tarjet = voice_g711

all: $(tarjet)

$(tarjet): $(objs)
	$(CXX) $(GFLAGS) -o $(tarjet) $(objs) -pthread -lm
	
install:
	cp $(tarjet) $(ROOT_PATH)/ejecs/$(tarjet)

clean:
	rm -f *.o *.d $(tarjet)

-include $(wildcard *.d)