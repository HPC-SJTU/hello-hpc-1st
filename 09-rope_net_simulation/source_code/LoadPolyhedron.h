 																	//

#ifndef _LOADPOLYHEDRON_H_
#define _LOADPOLYHEDRON_H_

#include <iostream>
#include <fstream>
#include <string>
#include <stdlib.h>
#include <cstdio>
#include <assert.h>
#include "math.h"

#include "constant.h"

using namespace std;

typedef struct polyhedron 
{
	int NumVerts, NumFaces, NumEdges;
	double Density;
	int *Faces, *Edges;
	double *Vertices, *EdgeLens, *EdgeNormVecs, *FaceNormVecs;
} POLYHEDRON;

void PolyhedronMemoryAlloc(POLYHEDRON& p);
void LoadPolyhedron(const char* filename, POLYHEDRON &p);

#endif