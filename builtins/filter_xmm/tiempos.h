#ifndef TIEMPOS_H_
#define TIEMPOS_H_


static __inline__ unsigned long long rdtsc(void)
{
	unsigned long long int x;
	__asm__ volatile (".byte 0x0f, 0x31" : "=A" (x));
	return x;
}

//#define CPU_KHZ	1798824.0 //vmware centos5
//#define CPU_KHZ	2790744.0 //desarrollo
#define CPU_KHZ	1729081.0 //mi toshiba
//#define CPU_KHZ	332949.0 //AMD Geode bajo

#define __tiempos_begin(tiempo) \
	static /*__thread*/ unsigned long long var_##tiempo = 0; \
	var_##tiempo = rdtsc();

#define __tiempos_end(tiempo, tid, veces) \
	static /*__thread*/ unsigned long long acum_##tiempo = 0; \
	static /*__thread*/ int count_##tiempo = 0; \
	acum_##tiempo += (rdtsc() - var_##tiempo); \
	count_##tiempo++; \
	if(count_##tiempo == veces) {\
		fprintf(stderr, "[:%d] Tiempo " #tiempo ": %0.3fms\n", tid, \
				(acum_##tiempo / (CPU_KHZ * veces))); \
		acum_##tiempo = 0; \
		count_##tiempo = 0; \
	}

#define __tiempos_triger(var) \
	static /*__thread*/ unsigned long long ss_##var = 0; \
	if(!ss_##var) ss_##var = rdtsc(); \
	int aux_##var = ((rdtsc() - ss_##var) / CPU_KHZ); \
	if(aux_##var >= (int)var) { \
		ss_##var = rdtsc(); \
		var = aux_##var; \
	} else { \
		var = 0; \
	}


#ifndef _TIEMPOS_LOOP
#define _TIEMPOS_LOOP 5
#endif

#endif /*TIEMPOS_H_*/
