
#include <stdio.h>


main()
{
	int var = 0x00;
	int r = __builtin_ffs(var);
	printf("ffs -> var: 0x%x, r: %d\n", var, r);
	var = 0x01;
	r = __builtin_ffs(var);
	printf("ffs -> var: 0x%x, r: %d\n", var, r);
	var = 0x080000;
	r = __builtin_ffs(var);
	printf("ffs -> var: 0x%x, r: %d\n", var, r);
	var = 0x80000000;
	r = __builtin_ffs(var);
	printf("ffs -> var: 0x%x, r: %d\n", var, r);
	var = 0x01;
	r = __builtin_clz(var);
	printf("clz -> var: 0x%x, r: %d\n", var, r);
	var = 0x080000;
	r = __builtin_clz(var);
	printf("clz -> var: 0x%x, r: %d\n", var, r);
	var = 0x80000000;
	r = __builtin_clz(var);
	printf("clz -> var: 0x%x, r: %d\n", var, r);
	var = 0x01;
	r = __builtin_ctz(var);
	printf("ctz -> var: 0x%x, r: %d\n", var, r);
	var = 0x080000;
	r = __builtin_ctz(var);
	printf("ctz -> var: 0x%x, r: %d\n", var, r);
	var = 0x80000000;
	r = __builtin_ctz(var);
	printf("ctz -> var: 0x%x, r: %d\n", var, r);
	var = 0x01;
	r = __builtin_popcount(var);
	printf("popcount -> var: 0x%x, r: %d\n", var, r);
	var = 0x080000;
	r = __builtin_popcount(var);
	printf("popcount -> var: 0x%x, r: %d\n", var, r);
	var = 0x80000000;
	r = __builtin_popcount(var);
	printf("popcount -> var: 0x%x, r: %d\n", var, r);
}

