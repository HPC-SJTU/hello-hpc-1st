.PHONY: all clean

all: bitmatrix

clean:
	rm -f bitmatrix

bitmatrix: main.cpp user.cpp common.h
	$(CXX) -O3 -std=c++20 -o $@ main.cpp user.cpp
