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
	movl	$1, %edx
	movl	%esp, %ebp
	pushl	%edi
	pushl	%esi
	pushl	%ebx
	subl	$8, %esp
	fnstcw	-14(%ebp)			#store x87 control word
	movl	12(%ebp), %edi			#edi=&z0
	fldl	.LC5
	fldl	.LC6
	leal	8(%edi), %esi			#esi=&z1
	movzwl	-14(%ebp), %eax
	leal	16(%edi), %ebx			#ebx=&z2
	leal	24(%edi), %ecx			#ecx=&z3
	movw	%ax, -18(%ebp)
	orw	$3072, -18(%ebp)
	movzwl	-18(%ebp), %eax
	movw	%ax, -16(%ebp)			#store alternative x87 control word
	movl	8(%ebp), %eax
	.p2align 4,,15
.L2:
	movl	8(%ebp), %eax
	filds	-2(%eax,%edx,2)
	fldl	.LC0
	fmul	%st(1), %st			#b0*x(i)
	fldl	(%edi)
	fadd	%st(1), %st			#y = b0*x(i) + z0
	fldl	.LC1
	fmul	%st(3), %st			#b1*x(i)
	fldl	(%esi)
	fadd	%st(1), %st			#b1*x(i) + z1
	fldl	.LC2
	fmul	%st(3), %st			#a1*y
	fsubrp	%st, %st(1)		#b1*x(i) + z1 - a1*y
	fstpl	(%edi)				#z0 = 
	fxch	%st(3)				#
	fmull	.LC3					#b2*x(i)
	faddl	(%ebx)				#b2*x(i) + z2
	fldl	.LC4
	fmul	%st(2), %st			#a2*y
	fsubrp	%st, %st(1)		#b2*x(i) + z2 - a2*y
	fstpl	(%esi)				#z1 = 
	fxch	%st(2)
	faddl	(%ecx)
	fld	%st(2)
	fmul	%st(5), %st
	fsubrp	%st, %st(1)
	fstpl	(%ebx)				#z2 = 
	fld	%st(1)
	fmul	%st(3), %st
	fsubrp	%st, %st(1)
	fstpl	(%ecx)				#z3 = 
#	fldcw	-16(%ebp)			#change alternative x87 mode (round up)
	fistps	-2(%eax,%edx,2) #x(i) =
#	fldcw	-14(%ebp)			#change normal x87 mode (round nearest)
	incl	%edx
	cmpl	$2049, %edx
	jne	.L2
	fstp	%st(0)
	fstp	%st(0)
	addl	$8, %esp
	popl	%ebx
	popl	%esi
	popl	%edi
	popl	%ebp
	ret
	.size	filter_n4k4, .-filter_n4k4
	.ident	"GCC: (GNU) 4.1.2 (Gentoo 4.1.2 p1.0.2)"
	.section	.note.GNU-stack,"",@progbits
