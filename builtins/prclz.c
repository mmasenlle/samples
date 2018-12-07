
#include <stdio.h>


main()
{
	int var,r;
	var = 0x0800;
	r = __builtin_clz(var);
	printf("clz -> var: 0x%x, r: %d\n", var, r);
	var = 0x080000;
	r = __builtin_clz(var);
	printf("clz -> var: 0x%x, r: %d\n", var, r);
	var = 0x80000000;
	r = __builtin_clz(var);
	printf("clz -> var: 0x%x, r: %d\n", var, r);
	var = 0x80000000;
	r = __builtin_popcount(var);
	printf("popcount -> var: 0x%x, r: %d\n", var, r);
}

