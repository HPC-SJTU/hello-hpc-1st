 																//

#ifndef _ODEEULER_H_
#define _ODEEULER_H_

#include "LoadPolyhedron.h"
#include "LoadFNS.h"
#include "acceleration.h"

void OdeEuler(double *y0, const double timestep, const double timestart, const double timeend, POLYHEDRON &p, FNS &fns, const double *SurfacePara, char* solution, double *FAC);

#endif