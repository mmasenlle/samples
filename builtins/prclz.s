	.file	"prclz.c"
	.section	.rodata
.LC0:
	.string	"clz -> var: 0x%x, r: %d\n"
.globl __popcountsi2
.LC1:
	.string	"popcount -> var: 0x%x, r: %d\n"
	.text
.globl main
	.type	main, @function
main:
	leal	4(%esp), %ecx
	andl	$-16, %esp
	pushl	-4(%ecx)
	pushl	%ebp
	movl	%esp, %ebp
	pushl	%ecx
	subl	$36, %esp
	movl	$2048, -12(%ebp)
	movl	-12(%ebp), %eax
	bsrl	%eax, %eax
	xorl	$31, %eax
	movl	%eax, -8(%ebp)
	movl	-8(%ebp), %eax
	movl	%eax, 8(%esp)
	movl	-12(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$.LC0, (%esp)
	call	printf
	movl	$524288, -12(%ebp)
	movl	-12(%ebp), %eax
	bsrl	%eax, %eax
	xorl	$31, %eax
	movl	%eax, -8(%ebp)
	movl	-8(%ebp), %eax
	movl	%eax, 8(%esp)
	movl	-12(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$.LC0, (%esp)
	call	printf
	movl	$-2147483648, -12(%ebp)
	movl	-12(%ebp), %eax
	bsrl	%eax, %eax
	xorl	$31, %eax
	movl	%eax, -8(%ebp)
	movl	-8(%ebp), %eax
	movl	%eax, 8(%esp)
	movl	-12(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$.LC0, (%esp)
	call	printf
	movl	$-2147483648, -12(%ebp)
	movl	-12(%ebp), %eax
	movl	%eax, (%esp)
	call	__popcountsi2
	movl	%eax, -8(%ebp)
	movl	-8(%ebp), %eax
	movl	%eax, 8(%esp)
	movl	-12(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	$.LC1, (%esp)
	call	printf
	addl	$36, %esp
	popl	%ecx
	popl	%ebp
	leal	-4(%ecx), %esp
	ret
	.size	main, .-main
	.ident	"GCC: (GNU) 4.1.2 (Gentoo 4.1.2 p1.0.2)"
	.section	.note.GNU-stack,"",@progbits
