
#include <stdio.h>
#include "tiempos.h"

main()
{
int expMask,i;
	int pcm = 0x4000;
	int exponent = 7;
	int exp2, exp3;
    //Move to the right and decrement exponent 

    //until we hit the 1 or the exponent hits 0

__tiempos_begin(for1);
    for(i=0;i<10000;i++)
    {
    pcm = 0x4000; exponent = 7;
    for (expMask = 0x4000; (pcm & expMask) == 0 
         && exponent>0; exponent--, expMask >>= 1) { }
         }
__tiempos_end(for1, 0, 1);
__tiempos_begin(clz1);
    for(i=0;i<10000;i++)
    {
    pcm = 0x4000;
    exp2 = 24 - __builtin_clz(pcm);}
__tiempos_end(clz1, 0, 1);
__tiempos_begin(clz12);
    for(i=0;i<10000;i++)
    {
    pcm = 0x4000;
    asm("bsrl %1, %0; xorl $31, %0" : "=r" (exp3) : "r" ((unsigned)pcm));
    exp3 = 24 -exp3;
    }
__tiempos_end(clz12, 0, 1); 
    printf("for: %d, builtin: %d, clz: %d\n", exponent, exp2, exp3);
__tiempos_begin(for2);
    for(i=0;i<10000;i++)
    {
    pcm = 0x400; exponent = 7;
        for (expMask = 0x4000; (pcm & expMask) == 0 
         && exponent>0; exponent--, expMask >>= 1) { }
         }
__tiempos_end(for2, 0, 1);
__tiempos_begin(clz2);         
    for(i=0;i<10000;i++)
    {
    pcm = 0x400;
    exp2 = 24 - __builtin_clz(pcm);
    }
__tiempos_end(clz2, 0, 1);    
__tiempos_begin(clz22);
    for(i=0;i<10000;i++)
    {
    pcm = 0x400;
    asm("bsrl %1, %0; xorl $31, %0; subrl $24, %0" : "=r" (exp3) : "r" ((unsigned)pcm));
    }
__tiempos_end(clz22, 0, 1); 
    printf("for: %d, builtin: %d, clz: %d\n", exponent, exp2, exp3);
        pcm = 0x0100; exponent = 7;
__tiempos_begin(for3);
    for(i=0;i<10000;i++)
    {
    pcm = 0x100; exponent = 7;
    for (expMask = 0x4000; (pcm & expMask) == 0 
         && exponent>0; exponent--, expMask >>= 1) { }
         }
__tiempos_end(for3, 0, 1);
__tiempos_begin(clz3);         
    for(i=0;i<10000;i++)
    {
    pcm = 0x100;
    exp2 = 24 - __builtin_clz(pcm);
    }
__tiempos_end(clz3, 0, 1);    
__tiempos_begin(clz32);
    for(i=0;i<10000;i++)
    {
    pcm = 0x100;
    asm("bsrl %1, %0; xorl $31, %0" : "=r" (exp3) : "r" ((unsigned)pcm));
    exp3 = 24 -exp3;
    }
__tiempos_end(clz32, 0, 1); 
    printf("for: %d, builtin: %d, clz: %d\n", exponent, exp2, exp3);
}

