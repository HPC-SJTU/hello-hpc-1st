 																//

#include "Initialize.h"
using namespace std;

void initialize(const char* filename_asteroid, const char* filename_SHPara, const char* filename_FNS,
	POLYHEDRON& PolySurface, double* SurfaceParam, FNS& fns) 
{
	LoadPolyhedron(filename_asteroid, PolySurface);
	LoadSHPara(filename_SHPara, SurfaceParam);
	LoadFNS(filename_FNS, fns);

}

void SetInitialConditions(double* initial_conditions, FNS& fns) {
	int id = 0;
	for (int j = 0; j < fns.NP; j++) {
		for (int k = 0; k < 3; k++) {
			initial_conditions[id] = fns.Pt[j + k * fns.NP];
			id++;
		}
	}

	for (int i = 3 * fns.NP; i < 6 * fns.NP; i = i + 3) {
		initial_conditions[i] = 0;
	}

	for (int i = 3 * fns.NP + 1; i < 6 * fns.NP; i = i + 3) {
		initial_conditions[i] = -10;
	}

	for (int i = 3 * fns.NP + 2; i < 6 * fns.NP; i = i + 3) {
		initial_conditions[i] = 0;
	}
}

void obtainFAC(double* FAC, const char* file_FAC) {
	FILE* infile;
	infile = fopen(file_FAC, "r");
	if (infile == NULL) {
		cerr << "Error opening file: " << file_FAC << endl;
		exit(EXIT_FAILURE);
	}
	for (int i = 0; i < 253; i++) {
		fscanf(infile, "%lf", &FAC[i]);
	}
	fclose(infile);
}