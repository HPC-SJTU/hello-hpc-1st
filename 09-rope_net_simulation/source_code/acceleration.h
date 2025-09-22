 									//

#ifndef _ACCELERATION_H_
#define _ACCELERATION_H_

#include "LoadPolyhedron.h"
#include "LoadFNS.h"
#include "SurfacePoints.h"
#include "calGF.h"

void calAcceleration(const double* solutionminusone,
	double* acceleration, const POLYHEDRON& p, 
	const FNS& fns, const double* SurfacePara, 
	double* FAC, double* theta, double* phi, double* r);
void CoorTran(const int VectorLength, const double* x, 
	const double* y, const double* z, double* theta, double* 
	phi, double* r);

#endif