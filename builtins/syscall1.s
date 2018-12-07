	.file	"syscall1.c"
	.text
.globl func
	.type	func, @function
func:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$16, %esp
	movl	$4, %eax
#APP
	int $0x80
#NO_APP
	movl	%eax, -4(%ebp)
	leave
	ret
	.size	func, .-func
	.ident	"GCC: (GNU) 4.1.1 (Gentoo 4.1.1)"
	.section	.note.GNU-stack,"",@progbits
