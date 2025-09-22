 																//

#include "OdeEuler.h"

void OdeEuler(double *y0, const double dt, const double tstart, const double tend, POLYHEDRON &p, FNS &fns, const double *SurfacePara, char* solution, double *FAC)
{
	int n = (int) floor((tend-tstart)/dt);
	double* result = new double[2*fns.NP*6];
	double* acceleration = new double[fns.NP*3];

	for (int j = 0; j < 6*fns.NP; j++){
		result[j]=y0[j];
	}

	FILE * infile;
	infile = fopen(solution, "w");
	for (int j = 0; j < fns.NP*6-1; j++){
		fprintf(infile, "%lf ", result[0+j]);
	}
	fprintf(infile, "%lf\n", result[0+(6*fns.NP-1)]);

	double* theta = new double[fns.NP * 1];
	double* phi = new double[fns.NP * 1];
	double* r = new double[fns.NP * 1];

	for (int i = 1; i < n; i++)
	{
		calAcceleration(&result[0], acceleration, p, fns, SurfacePara, FAC, theta, phi, r);

		for (int j = 0; j < fns.NP; j++){
			result[6*fns.NP+(3*j+fns.NP*3)]   = result[(3*j+fns.NP*3)]  +dt*acceleration[3*j];
			result[6*fns.NP+(3*j+1+fns.NP*3)] = result[(3*j+1+fns.NP*3)]+dt*acceleration[3*j+1];
			result[6*fns.NP+(3*j+2+fns.NP*3)] = result[(3*j+2+fns.NP*3)]+dt*acceleration[3*j+2];
			result[6*fns.NP+(3*j)]   = result[(3*j)]  +dt*result[6*fns.NP+(3*j+fns.NP*3)];
			result[6*fns.NP+(3*j+1)] = result[(3*j+1)]+dt*result[6*fns.NP+(3*j+1+fns.NP*3)];
			result[6*fns.NP+(3*j+2)] = result[(3*j+2)]+dt*result[6*fns.NP+(3*j+2+fns.NP*3)];
		}

		if (i%1000==0){
			for (int j = 0; j < fns.NP*6-1; j++){
				fprintf(infile, "%lf ", result[6*fns.NP+j]);
			}
			fprintf(infile, "%lf\n", result[6*fns.NP+(6*fns.NP-1)]);
		}

		//
		for (int j = 0; j < 6*fns.NP; j++){
			result[j] = result[j+fns.NP*6];
		}
	}

	delete[] theta; theta = NULL;
	delete[] phi;  phi = NULL;
	delete[] r;    r = NULL;

	fclose(infile);

	delete[] result;         result = NULL;
	delete[] acceleration;     acceleration = NULL;
}