 																	//

#ifndef _LOADFNS_H_
#define _LOADFNS_H_

#include <math.h>
#include <stdlib.h>
#include <cstdio>
#include <assert.h>
#include <memory>

using namespace std;

typedef struct FlexibleNetSpacecraft
{
	int NP, NumEdges, NumRopeNodes, col_Topo;
	double Radius;
	int *Ed, *TP;
	double *Pt, *EL, *BL;
} FNS;

void LoadFNS(const char* filename, FNS &fns);
void FNSMemoryAlloc(FNS &fns);

#endif