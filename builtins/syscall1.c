int func(void)
{
long __res;
__asm__ volatile ("int $0x80"	: "=a" (__res)	: "0" (4));
}
