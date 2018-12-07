	.file	"fclz.c"
	.text
.globl fclz
	.type	fclz, @function
fclz:
	pushl	%ebp
	movl	%esp, %ebp
	movl	8(%ebp), %eax
	bsrl	%eax, %eax
	xorl	$31, %eax
	popl	%ebp
	ret
	.size	fclz, .-fclz
.globl fclz2
	.type	fclz2, @function
fclz2:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$16, %esp
#APP
	bsfl 8(%ebp), -4(%ebp); xorl $31, -4(%ebp)
#NO_APP
	movl	-4(%ebp), %eax
	leave
	ret
	.size	fclz2, .-fclz2
	.ident	"GCC: (GNU) 4.1.2 (Gentoo 4.1.2 p1.0.2)"
	.section	.note.GNU-stack,"",@progbits
