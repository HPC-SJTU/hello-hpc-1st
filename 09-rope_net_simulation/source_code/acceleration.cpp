 
#include "acceleration.h"

void calAcceleration(const double* solutionminusone,
	double* acceleration, const POLYHEDRON& p, 
	const FNS& fns, const double* SurfacePara, 
	double* FAC, double* theta, double* phi, double* r)
{   
	
	int if_colli = 0;
		//
	double 	sfR = 0, NVx = 0, NVy = 0, NVz = 0, 
		 	NVt = 0, NVp = 0, tmp1 = 0, tmp2 = 0, 
		 	dzs = 0, vzs = 0;
	double fp[3] = { 0 }, GravF[3] = { 0 }, Nf[3] = { 0 }, ff[3] = { 0 }, tmp3[3] = { 0 }, tmp4[3] = { 0 }, force[3] = { 0 };


	for (int i = 0; i < fns.NP; i++) {
		

		CoorTran(1, &solutionminusone[3 * i], &solutionminusone[(3 * i + 1)], &solutionminusone[(3 * i + 2)], &theta[i], &phi[i], &r[i]);
		SurfacePoints(theta[i], phi[i], SurfacePara, sfR, NVx, NVy, NVz, FAC);
		CoorTran(1, &NVx, &NVy, &NVz, &NVt, &NVp, &tmp1);

		fp[0] = solutionminusone[3 * i]; fp[1] = solutionminusone[(3 * i + 1)]; fp[2] = solutionminusone[(3 * i + 2)];
		GravAttraction(p, fp, GravF);
		GravF[0] *= Pm * G * p.Density;    GravF[1] *= Pm * G * p.Density;     GravF[2] *= Pm * G * p.Density;

		//
		dzs = r[i] - sfR;
		vzs = solutionminusone[(3 * i + fns.NP * 3)] * NVx + solutionminusone[(3 * i + 1 + fns.NP * 3)] * NVy + solutionminusone[(3 * i + 2 + fns.NP * 3)] * NVz;
		if (dzs > 0) {
			if_colli = 0;
		}
		else {
			if_colli = 1;
		}

		tmp1 = Ki * abs(dzs) * if_colli;
		tmp2 = -1 * Ci * vzs * if_colli;
		Nf[0] = (tmp1 + tmp2) * sin(NVt) * cos(NVp);
		Nf[1] = (tmp1 + tmp2) * sin(NVt) * sin(NVp);
		Nf[2] = (tmp1 + tmp2) * cos(NVt);
		tmp3[0] = solutionminusone[(3 * i + fns.NP * 3)] * (1 - sin(NVt) * cos(NVp));
		tmp3[1] = solutionminusone[(3 * i + 1 + fns.NP * 3)] * (1 - sin(NVt) * sin(NVp));
		tmp3[2] = solutionminusone[(3 * i + 2 + fns.NP * 3)] * (1 - cos(NVt));
		CoorTran(1, &tmp3[0], &tmp3[1], &tmp3[2], &tmp4[0], &tmp4[1], &tmp4[2]);
		ff[0] = (-1 * miu) * (tmp1 + tmp2) * sin(tmp4[0]) * cos(tmp4[1]);
		ff[1] = (-1 * miu) * (tmp1 + tmp2) * sin(tmp4[0]) * sin(tmp4[1]);
		ff[2] = (-1 * miu) * (tmp1 + tmp2) * cos(tmp4[0]);

		for (int j = 0; j < fns.TP[i]; j++) {
			tmp3[0] = solutionminusone[3 * fns.TP[i + (2 * j + 2) * fns.NP]] - solutionminusone[3 * i];              // dr
			tmp3[1] = solutionminusone[(3 * fns.TP[i + (2 * j + 2) * fns.NP] + 1)] - solutionminusone[(3 * i + 1)];
			tmp3[2] = solutionminusone[(3 * fns.TP[i + (2 * j + 2) * fns.NP] + 2)] - solutionminusone[(3 * i + 2)];
			tmp4[0] = solutionminusone[(3 * fns.TP[i + (2 * j + 2) * fns.NP] + 0 + fns.NP * 3)] - solutionminusone[(3 * i + 0 + fns.NP * 3)];              // dv
			tmp4[1] = solutionminusone[(3 * fns.TP[i + (2 * j + 2) * fns.NP] + 1 + fns.NP * 3)] - solutionminusone[(3 * i + 1 + fns.NP * 3)];
			tmp4[2] = solutionminusone[(3 * fns.TP[i + (2 * j + 2) * fns.NP] + 2 + fns.NP * 3)] - solutionminusone[(3 * i + 2 + fns.NP * 3)];

			tmp1 = sqrt(tmp3[0] * tmp3[0] + tmp3[1] * tmp3[1] + tmp3[2] * tmp3[2]);  // ndr
			tmp3[0] /= tmp1;   tmp3[1] /= tmp1;  tmp3[2] /= tmp1;  // udr
			if (tmp1 - fns.EL[fns.TP[i + (2 * j + 1) * fns.NP]] > 0) {
				tmp2 = tmp4[0] * tmp3[0] + tmp4[1] * tmp3[1] + tmp4[2] * tmp3[2];
				force[0] += ki * (tmp1 - fns.EL[fns.TP[i + (2 * j + 1) * fns.NP]]) * tmp3[0] + ci * tmp2 * tmp3[0];
				force[1] += ki * (tmp1 - fns.EL[fns.TP[i + (2 * j + 1) * fns.NP]]) * tmp3[1] + ci * tmp2 * tmp3[1];
				force[2] += ki * (tmp1 - fns.EL[fns.TP[i + (2 * j + 1) * fns.NP]]) * tmp3[2] + ci * tmp2 * tmp3[2];
			}
		}
		acceleration[0 + i * 3] = (force[0] + GravF[0] + Nf[0] + ff[0]) / Pm;
		acceleration[1 + i * 3] = (force[1] + GravF[1] + Nf[1] + ff[1]) / Pm;
		acceleration[2 + i * 3] = (force[2] + GravF[2] + Nf[2] + ff[2]) / Pm;

	}
}

inline void CoorTran(const int VectorLength, const double* x, const double* y, const double* z, double* theta, double* phi, double* r)
{
	int i;
	for (i = 0; i < VectorLength; i++) {
		theta[i] = PI / 2 - atan2(z[i], sqrt(x[i] * x[i] + y[i] * y[i]));
	}
	for (i = 0; i < VectorLength; i++) {
		phi[i] = atan2(y[i], x[i]);
		if (phi[i] < 0) {
			phi[i] += 2 * PI;
		}
	}
	for (i = 0; i < VectorLength; i++) {
		r[i] = sqrt(x[i] * x[i] + y[i] * y[i] + z[i] * z[i]);
	}
}
