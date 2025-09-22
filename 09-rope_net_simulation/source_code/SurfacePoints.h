 													//

#ifndef _SURFACEPOINTS_H_
#define _SURFACEPOINTS_H_

#include "LoadPolyhedron.h"
#include "LoadFNS.h"
#include "SurfacePoints.h"

void SurfacePoints(const double theta, const double phi, const double* SurfacePara, double &SurfaceR, double &NormalVecx, double &NormalVecy, double &NormalVecz, double* FAC);
double LegendreP(const int BigL, const int SmallM, const double Variable);
int factorial(const int a);

#endif