	.file	"filter_c.c"
	.section	.rodata.cst8,"aM",@progbits,8
	.align 8
.LC0:								#b0 b4
	.long	-922765134
	.long	1065674868
	.align 8
.LC1:								#b1 b3
	.long	-455197814
	.long	1067772087
	.align 8
.LC2:								#a1
	.long	1957130697
	.long	-1073774928
	.align 8
.LC3:								#b2
	.long	-682796721
	.long	1068457235
	.align 8
.LC4:								#a2
	.long	581366773
	.long	1073464853
	.align 8
.LC5:								#a3
	.long	-1247945698
	.long	-1075368229
	.align 8
.LC6:								#a4
	.long	147059680
	.long	1069470177
	.text
	.p2align 4,,15
.globl filter_n4k4
	.type	filter_n4k4, @function
filter_n4k4:
	pushl	%ebp
	movl	$1, %edx					#edx=i
	movl	%esp, %ebp
	pushl	%edi
	pushl	%esi
	pushl	%ebx
	movl	12(%ebp), %edi			#edi=&z0
	leal	8(%edi), %esi			#esi=&z1
	leal	16(%edi), %ebx			#ebx=&z2
	leal	24(%edi), %ecx			#ecx=&z3
	movl	8(%ebp), %eax			#eax=x
	fldl	(%ecx)
	fldl	(%ebx)
	fldl	(%esi)
	fldl	(%edi)
	.p2align 4,,15
.L2:									#z3, z2, z1, z0
	filds	-2(%eax,%edx,2)		#z3, z2, z1, z0, x(i)
	fldl	.LC0
	fmul	%st(1), %st			#b0*x(i)
	fadd	%st(2), %st			#b0*x(i) + z0		#z3, z2, z1, z0, x(i), y, _ , _
	fldl	.LC1
	fmul	%st(2), %st			#b1*x(i)
	fadd	%st(4), %st			#b1*x(i) + z1
	fldl	.LC2
	fmul	%st(2), %st			#a1*y
	fsubrp	%st, %st(1)		#b1*x(i) + z1 - a1*y
	fstp	%st(3)				#z0 =
	fldl	.LC3
	fmul	%st(2), %st			#b2*x(i)
	fadd	%st(5), %st			#b2*x(i) + z2
	fldl	.LC4
	fmul	%st(2), %st			#a2*y
	fsubrp	%st, %st(1)		#b2*x(i) + z2 - a2*y
	fstp	%st(4)				#z1 =
	fldl	.LC1
	fmul	%st(2), %st			#b3*x(i)
	fadd	%st(6), %st			#b3*x(i) + z3
	fldl	.LC5
	fmul	%st(2), %st			#a3*y
	fsubrp	%st, %st(1)		#b3*x(i) + z3 - a3*y
	fstp	%st(5)				#z2 =
	fldl	.LC0
	fmul	%st(2), %st			#b4*x(i)
	fldl	.LC6
	fmul	%st(2), %st			#a4*y
	fsubrp	%st, %st(1)		#b4*x(i) - a4*y
	fstp	%st(6)				#z3 =
	fistps	-2(%eax,%edx,2) #x(i) = y
	fstp	%st(0)				#remove x
	incl	%edx
	cmpl	$2049, %edx
	jne	.L2
	fstpl	(%edi)
	fstpl	(%esi)
	fstpl	(%ebx)
	fstpl	(%ecx)				#restore z
	popl	%ebx
	popl	%esi
	popl	%edi
	popl	%ebp
	ret
	.size	filter_n4k4, .-filter_n4k4
	.ident	"GCC: (GNU) 4.1.2 (Gentoo 4.1.2 p1.0.2)"
	.section	.note.GNU-stack,"",@progbits
