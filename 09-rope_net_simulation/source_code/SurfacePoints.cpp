 															//

#include "SurfacePoints.h"

void SurfacePoints(const double theta, const double phi, const double* SurfacePara, double &SurfaceR, double &NormalVecx, double &NormalVecy, double &NormalVecz, double* FAC)
{
	int i, m, k, len, id;
	double tmp;
	
	len = (SHdegree+1)*(SHdegree+2)/2;

	double* CS = new double[len*2];
	for (i = 0; i < len; i++){
		CS[i]=SurfacePara[(SHlmax+1)*(SHlmax+2)/2*2+i];
		CS[len+i]=SurfacePara[(SHlmax+1)*(SHlmax+2)/2*3+i];
	}

	double* PS = new double[len];
	for (i = 0; i < len; i++){
		PS[i] = 0.0;
	}

	for (k = 0; k <= SHdegree; k++){
		for (i = k*(k+1)/2; i<(k+1)*(k+2)/2; i++){
			PS[i]=LegendreP(k, i-(k*(k+1)/2), cos(theta));
		}
	}

	double* KS = new double[len];
	for (i = 0; i < len; i++){
		KS[i] = 0.0;
	}
	id = 0;
	for (k = 0; k <= SHdegree; k++){
		for (m = 0; m <= k; m++){
			tmp = FAC[id];
			KS[id] = sqrt(((2*(double)k+1)/4/PI)*tmp);
			id += 1;
		}
	}

	// SurfaceR
	SurfaceR = 0;
	id = 0;
	for (k = 0; k <= SHdegree; k++){
		for (m = 0; m <= k; m++){
			if (m){
				double tmp1 = sin(k*phi);
				tmp = sqrt(2)*PS[id]*KS[id]*(cos(m*phi)*CS[id]+sin(m*phi)*CS[id+len]);
			}
			else{
				tmp = PS[id]*KS[id]*CS[id];
			}
			SurfaceR += tmp;
			id += 1;
		}
	}
	
	// SurfaceX, SurfaceY, SurfaceZ
	double SurfaceX = SurfaceR*sin(theta)*cos(phi);
	double SurfaceY = SurfaceR*sin(theta)*sin(phi);
	double SurfaceZ = SurfaceR*cos(theta);

	// PS 
	for (i = 0; i < len; i++){
		PS[i] = 0.0;
	}
	for (k = 0; k <= SHdegree; k++){
		for (i = k*(k+1)/2; i<(k+1)*(k+2)/2; i++){
			m=i-k*(k+1)/2;
			PS[i] = LegendreP(k,m,cos(theta))*(-1*((k+1)*cos(theta))/(cos(theta)*cos(theta)-1))+LegendreP(k+1,m,cos(theta))*((k-m+1)/(cos(theta)*cos(theta)-1));
			PS[i]*= -1*sin(theta);	
		}
	}

	// dS_dtheta
	double S_theta = 0;
	id = 0;
	for (k = 0; k <= SHdegree; k++){
		for (m = 0; m <= k; m++){
			if (m){
				tmp = sqrt(2)*PS[id]*KS[id]*(cos(m*phi)*CS[id]+sin(m*phi)*CS[id+len]);
			}
			else{
				tmp = PS[id]*KS[id]*CS[id];
			}
			S_theta += tmp;
			id += 1;
		}
	}

	// PS 
	for (i = 0; i < len; i++){
		PS[i] = 0.0;
	}
	for (k = 0; k <= SHdegree; k++){
		for (i = k*(k+1)/2; i<(k+1)*(k+2)/2; i++){
			m=i-k*(k+1)/2;
			PS[i] = LegendreP(k,m,cos(theta))*(-1*m);		
		}
	}

	// dS_dtheta
	double S_phi = 0;
	id = 0;
	for (k = 0; k <= SHdegree; k++){
		for (m = 0; m <= k; m++){
			if (m){
				tmp = sqrt(2)*PS[id]*KS[id]*(sin(m*phi)*CS[id]-cos(m*phi)*CS[id+len]);
			}
			else{
				tmp = PS[id]*KS[id]*CS[id];
			}
			S_phi += tmp;
			id += 1;
		}
	}

	// tangent vector 1
	double TX1, TY1, TZ1;
	TX1=S_theta*sin(theta)*cos(phi)+SurfaceR*cos(theta)*cos(phi);
	TY1=S_theta*sin(theta)*sin(phi)+SurfaceR*cos(theta)*sin(phi);
	TZ1=S_theta*cos(theta)-SurfaceR*sin(theta);
	if (theta < 0.1){
		TX1 = 1;
		TY1 = 0;
		TZ1 = 0;
	}
	if (theta > 0.99*PI){
		TX1 = 0;
		TY1 = 1;
		TZ1 = 0;
	}
	tmp = sqrt(TX1*TX1+TY1*TY1+TZ1*TZ1);
	TX1 /= tmp;
	TY1 /= tmp;
	TZ1 /= tmp;

	// tangent vector 2
	double TX2, TY2, TZ2;
	TX2=S_phi*sin(theta)*cos(phi)-SurfaceR*sin(theta)*sin(phi);
	TY2=S_phi*sin(theta)*sin(phi)+SurfaceR*sin(theta)*cos(phi);
	TZ2=S_phi*cos(theta);
	if (theta < 0.1){
		TX2 = 0;
		TY2 = 1;
		TZ2 = 0;
	}
	if (theta > 0.99*PI){
		TX2 = 1;
		TY2 = 0;
		TZ2 = 0;
	}
	tmp = sqrt(TX2*TX2+TY2*TY2+TZ2*TZ2);
	TX2 /= tmp;
	TY2 /= tmp;
	TZ2 /= tmp;

	// normal vector 
	NormalVecx=TY1*TZ2-TY2*TZ1;
	NormalVecy=TX2*TZ1-TX1*TZ2;
	NormalVecz=TX1*TY2-TX2*TY1;
	tmp=sqrt(NormalVecx*NormalVecx+NormalVecy*NormalVecy+NormalVecz*NormalVecz);
	NormalVecx /= tmp;
	NormalVecy /= tmp;
	NormalVecz /= tmp;

	// justify the direction of the normal vector away from the asteroid
	tmp=SurfaceX*NormalVecx+SurfaceY*NormalVecy+SurfaceZ*NormalVecz;
	if (!tmp){
		NormalVecx *= -1;
		NormalVecy *= -1;
		NormalVecz *= -1;
	}

	delete[] CS;    CS = NULL;
	delete[] PS;    PS = NULL;
	delete[] KS;    KS = NULL;
}


// legendre function : P(n,m,x)=[(-1)^m]*[(1-x^2)^(m/2)]*[d^m(P(n,x))/dx^m], p(n,x)=1/[n!*2^n]*{d^n[(x^2-1)^n]/dx^n}.
double LegendreP(const int BigL, const int SmallM, const double Variable)
{
	bool flag=(SmallM<0||BigL<0||fabs(Variable)>1.0);
	if(flag)
		std::cout<<"����������������õ¶���ʽ��Ҫ��"<<std::endl;
	assert(!flag);
	if(BigL<SmallM)
		return 0;
	else
	{
		double PValue=1.0;
		if(SmallM>0)
		{
			double h=sqrt((1.0-Variable)*(1.0+Variable));
			double f=1.0;
			for(int i=1;i<=SmallM;i++)
			{
				PValue*=-f*h;
				f+=2.0;
			}
		}
		if(BigL==SmallM)
			return PValue;
		else
		{
			double PValuep1=Variable*(2*SmallM+1)*PValue;
			if(BigL==(SmallM+1))
				return PValuep1;
			else
			{
				double PLL=0.0;
				for(int LL=SmallM+2;LL<=BigL;LL++)
				{
					PLL=(Variable*(2*LL-1)*PValuep1-(LL+SmallM-1)*PValue)/(LL-SmallM);
					PValue=PValuep1;
					PValuep1=PLL;
				}
				return PLL;
			}
		}
	}
}

// factorial function
int factorial(const int a)
{
	int i, s = 1;
	if (a) {
		for (i=1; i<=a; i++) {
			s*=i;
		} 
	}
	else{
		s=1;
	}
	return s;
}