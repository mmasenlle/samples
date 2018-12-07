	.file	"filter_c.c"
	.section	.rodata.cst8,"aM",@progbits,8
	.align 8
.LC0:
	.long	-922765134
	.long	1065674868
	.align 8
.LC1:
	.long	-455197814
	.long	1067772087
	.align 8
.LC2:
	.long	1957130697
	.long	-1073774928
	.align 8
.LC3:
	.long	-682796721
	.long	1068457235
	.align 8
.LC4:
	.long	581366773
	.long	1073464853
	.align 8
.LC5:
	.long	-1247945698
	.long	-1075368229
	.align 8
.LC6:
	.long	147059680
	.long	1069470177
	.text
	.p2align 4,,15
.globl filter_n4k4
	.type	filter_n4k4, @function
filter_n4k4:
	pushl	%ebp
	movl	$1, %edx
	movl	%esp, %ebp
	pushl	%edi
	pushl	%esi
	pushl	%ebx
	subl	$28, %esp
	movl	12(%ebp), %edi
	fldl	.LC5
	fldl	.LC6
	leal	24(%edi), %eax
	leal	8(%edi), %esi
	leal	16(%edi), %ebx
	movl	%eax, -36(%ebp)
	.p2align 4,,15
.L2:
	movl	8(%ebp), %ecx
	movl	-36(%ebp), %eax
	filds	-2(%ecx,%edx,2)
	fldl	.LC0
	fmul	%st(1), %st
	fldl	(%edi)
	fadd	%st(1), %st
	fldl	.LC1
	fmul	%st(3), %st
	fldl	(%esi)
	fadd	%st(1), %st
	fldl	.LC2
	fmul	%st(3), %st
	fsubrp	%st, %st(1)
	fstpl	(%edi)
	fxch	%st(3)
	fmull	.LC3
	faddl	(%ebx)
	fldl	.LC4
	fmul	%st(2), %st
	fsubrp	%st, %st(1)
	fstpl	(%esi)
	fxch	%st(2)
	faddl	(%eax)
	fld	%st(2)
	fmul	%st(5), %st
	fsubrp	%st, %st(1)
	fstpl	(%ebx)
	fld	%st(1)
	fmul	%st(3), %st
	fsubrp	%st, %st(1)
	fstpl	(%eax)
	movl	8(%ebp), %eax
	fstpl	-24(%ebp)
	movsd	-24(%ebp), %xmm0
	cvttsd2si	%xmm0, %ecx
	movw	%cx, -2(%eax,%edx,2)
	incl	%edx
	cmpl	$2049, %edx
	jne	.L2
	fstp	%st(0)
	fstp	%st(0)
	addl	$28, %esp
	popl	%ebx
	popl	%esi
	popl	%edi
	popl	%ebp
	ret
	.size	filter_n4k4, .-filter_n4k4
	.ident	"GCC: (GNU) 4.1.2 (Gentoo 4.1.2 p1.0.2)"
	.section	.note.GNU-stack,"",@progbits
