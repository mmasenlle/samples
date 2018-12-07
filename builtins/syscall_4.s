msg: .string "Hola mapucho\n"
.globl main
main:
	movl $4,%eax
	movl $1,%ebx
	movl $msg,%ecx
	movl $13,%edx
	int $0x80
