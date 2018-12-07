	.file	"filter_c.c"
	.section	.rodata
	.align 32
	.type	a, @object
	.size	a, 40
a:
	.long	0
	.long	1072693248
	.long	1957130697
	.long	-1073774928
	.long	581366773
	.long	1073464853
	.long	-1247945698
	.long	-1075368229
	.long	147059680
	.long	1069470177
	.align 32
	.type	b, @object
	.size	b, 40
b:
	.long	-922765134
	.long	1065674868
	.long	-455197814
	.long	1067772087
	.long	-682796721
	.long	1068457235
	.long	-455197814
	.long	1067772087
	.long	-922765134
	.long	1065674868
	.text
.globl filter_n4k4
	.type	filter_n4k4, @function
filter_n4k4:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$24, %esp
	movl	$0, -12(%ebp)
	movl	$0, -12(%ebp)
	jmp	.L2
.L3:
	fldl	b
	movl	-12(%ebp), %eax
	addl	%eax, %eax
	addl	8(%ebp), %eax
	movswl	(%eax),%eax
	pushl	%eax
	filds	(%esp)
	leal	4(%esp), %esp
	fmulp	%st, %st(1)
	movl	12(%ebp), %eax
	fldl	(%eax)
	faddp	%st, %st(1)
	fstpl	-8(%ebp)
	fldl	b+8
	movl	-12(%ebp), %eax
	addl	%eax, %eax
	addl	8(%ebp), %eax
	movswl	(%eax),%eax
	pushl	%eax
	filds	(%esp)
	leal	4(%esp), %esp
	fmulp	%st, %st(1)
	movl	12(%ebp), %eax
	addl	$8, %eax
	fldl	(%eax)
	faddp	%st, %st(1)
	fldl	a+8
	fmull	-8(%ebp)
	fsubrp	%st, %st(1)
	movl	12(%ebp), %eax
	fstpl	(%eax)
	movl	12(%ebp), %edx
	addl	$8, %edx
	fldl	b+16
	movl	-12(%ebp), %eax
	addl	%eax, %eax
	addl	8(%ebp), %eax
	movswl	(%eax),%eax
	pushl	%eax
	filds	(%esp)
	leal	4(%esp), %esp
	fmulp	%st, %st(1)
	movl	12(%ebp), %eax
	addl	$16, %eax
	fldl	(%eax)
	faddp	%st, %st(1)
	fldl	a+16
	fmull	-8(%ebp)
	fsubrp	%st, %st(1)
	fstpl	(%edx)
	movl	12(%ebp), %edx
	addl	$16, %edx
	fldl	b+24
	movl	-12(%ebp), %eax
	addl	%eax, %eax
	addl	8(%ebp), %eax
	movswl	(%eax),%eax
	pushl	%eax
	filds	(%esp)
	leal	4(%esp), %esp
	fmulp	%st, %st(1)
	movl	12(%ebp), %eax
	addl	$24, %eax
	fldl	(%eax)
	faddp	%st, %st(1)
	fldl	a+24
	fmull	-8(%ebp)
	fsubrp	%st, %st(1)
	fstpl	(%edx)
	movl	12(%ebp), %edx
	addl	$24, %edx
	fldl	b+32
	movl	-12(%ebp), %eax
	addl	%eax, %eax
	addl	8(%ebp), %eax
	movswl	(%eax),%eax
	pushl	%eax
	filds	(%esp)
	leal	4(%esp), %esp
	fmulp	%st, %st(1)
	fldl	a+32
	fmull	-8(%ebp)
	fsubrp	%st, %st(1)
	fstpl	(%edx)
	movl	-12(%ebp), %eax
	addl	%eax, %eax
	movl	%eax, %edx
	addl	8(%ebp), %edx
	fldl	-8(%ebp)
	fnstcw	-18(%ebp)
	movzwl	-18(%ebp), %eax
	orw	$3072, %ax
	movw	%ax, -20(%ebp)
	fldcw	-20(%ebp)
	fistps	-22(%ebp)
	fldcw	-18(%ebp)
	movzwl	-22(%ebp), %eax
	cwtl
	movw	%ax, (%edx)
	incl	-12(%ebp)
.L2:
	cmpl	$2047, -12(%ebp)
	jle	.L3
	leave
	ret
	.size	filter_n4k4, .-filter_n4k4
	.ident	"GCC: (GNU) 4.1.2 (Gentoo 4.1.2 p1.0.2)"
	.section	.note.GNU-stack,"",@progbits
