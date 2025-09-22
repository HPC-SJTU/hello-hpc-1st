#include "LoadPolyhedron.h"
#include "SHPara.h"
#include "LoadFNS.h"
#include "Initialize.h"
#include "OdeEuler.h"
#include <iostream>
#include <cstdlib>
#include <chrono>
#include <fstream>


using namespace std;
using namespace chrono;

int main(int argc, char* argv[])
{   
	// Parse command line arguments for dt, t0, tf
	double dt = 1e-2;  // default value
	double t0 = 0.0;   // default value
	double tf = 1.0;   // default value
	
	if (argc >= 4) {
		dt = atof(argv[1]);
		t0 = atof(argv[2]);
		tf = atof(argv[3]);
	}
	
	auto start = system_clock::now(); 

	POLYHEDRON asteroid;
	FNS fns;
	double* SurfacePara = new double[(SHlmax + 1) * (SHlmax + 2) / 2 * 4];
	double* InitialConditions;

	initialize("./poly.txt",
		"./Shp.txt", 
		"./topo.txt", 
		asteroid, SurfacePara, fns);
	InitialConditions = new double[6 * fns.NP];
	SetInitialConditions(InitialConditions, fns);

	double* FAC = new double[253];
	obtainFAC(FAC, "./fact.txt");

	char output_file[] = "./Solution/result.txt";


	cout << "ODE with dt=" << dt << ", t0=" << t0 << ", tf=" << tf << endl;
	OdeEuler(InitialConditions, dt, t0, tf, asteroid, fns, SurfacePara, output_file, FAC);



	delete[] SurfacePara;           SurfacePara = NULL;
	delete[] InitialConditions;     InitialConditions = NULL;

	auto end   = system_clock::now();
	auto duration = duration_cast<microseconds>(end - start);
	cout <<  "花费了"
     		<< double(duration.count()) * microseconds::period::num / microseconds::period::den
     		<< "秒" << endl;
}
