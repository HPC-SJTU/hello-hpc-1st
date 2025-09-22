 																//

#ifndef INITIALIZE_H
#define INITIALIZE_H

#include "LoadPolyhedron.h"
#include "SHPara.h"
#include "LoadFNS.h"

void initialize(const char* filename_asteroid, const char* filename_SHPara, const char* filename_FNS,
	POLYHEDRON& PolySurface,double* SurfaceParam, FNS& fns);

void SetInitialConditions(double* initial_conditions, FNS& fns);

void obtainFAC(double* FAC, const char* file_FAC);

#endif