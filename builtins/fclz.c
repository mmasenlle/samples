

int fclz(int x)
{
	return __builtin_clz(x);
}

int fclz2(int x)
{
	int r;
	asm("bsrl %1, %0\n\t xorl $31, %0" : "=r" (r) : "r" (x));
	return r;
}

