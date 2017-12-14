SRCS := $(wildcard *.cpp)
CXX = g++
CXX_FLAGS = -std=c++11 -Wall -O3
OBJS = $(SRCS:.cpp=.o)
EXECUTABLES = $(SRCS:.cpp=)
RM = rm -f

%.o : %.cpp
	$(CXX) $(CXX_FLAGS) -c -o $@ $^

all: $(EXECUTABLES)

clean:
	$(RM) $(OBJS) $(EXECUTABLES)

parser.o: parser.cpp parser.hh
	$(CXX) $(CXX_FLAGS) -c -o $@ $<

runner_parser: parser.o runner_parser.o
	$(CXX) $(CXX_FLAGS) -o $@ $^ $(LIBS)
