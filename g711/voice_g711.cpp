
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/ioctl.h>
#include <sys/soundcard.h>
#include <sys/mman.h>
#include <pthread.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "utils.h"
#include "versionlit.h"
//#include "tiempos.h"


#ifdef _ARM_LIT
#define S2A_EXP(__s, __e) do { __e = __builtin_clz(__s); } while(0)
#else
#define S2A_EXP(__s, __e) asm("bsrl %1, %0\n\t xorl $31, %0" : "=r" (__e) : "r" ((int)(__s)));
#endif

#define SHORT2ALAW(_a, _s) \
do { \
	int exp, sign = ((_s) & 0x8000) >> 8; \
	if(sign) (_s) = -(_s); \
	if((_s) > 32635) (_s) = 32635; \
	S2A_EXP(_s, exp); \
	exp = (exp < 24) ? (24 - exp) : 0; \
	int mantissa = ((_s) >> ((exp == 0) ? 4 : (exp + 3))) & 0x0f; \
	(_a) = ((char)(sign | exp << 4 | mantissa)) ^ 0xd5; \
} while(0)

#define ALAW2SHORT(_s, _a) \
do { \
    (_a) ^= 0xd5; \
    int sign = (_a) & 0x80; \
    int exp = ((_a) & 0x70) >> 4; \
    int data = (((_a) & 0x0f) << 4) + 8; \
    if(exp != 0) data += 0x100; \
    if(exp > 1) data <<= (exp - 1); \
	(_s) = (short)(sign ? -data : data); \
} while(0)

static int fd_dsp = -1;
static int fd_udp = -1;

static struct sockaddr_in remote = { 0 };

static int verb = 0, fsize = 2048, trun = 1, use_fifo = 0, ndelay = 1,
	mute = 31, umb = 98, xlen = 160, delta = 1, xmlen = 512;

struct bufitem_t
{
	short l;
	short r;
};

#define BUF_IND_MAX 12
#define BUF_TAM 	((1 << (BUF_IND_MAX)) / sizeof(bufitem_t))
#define FSIZE_LEN 	(fsize/sizeof(bufitem_t))

#define MAX_X  512
#define MAX_XM 1024
#define XM_GAP 128
#define XM0    2500

//butter(4, .075, 'high')
static const double a[] = { 1.0, -3.384972728303895, 4.337061817421338, -2.489138293812544, .5393551282803071 };
static const double b[] = { .7344079979886303, -2.937631991954521, 4.406447987931782, -2.937631991954521, .7344079979886303 };

static double z[4];
static double x[MAX_X];
static double xm[MAX_XM];


#define SFIFO_LEN 4000
static int fifo_i = 0, fifo_j = 0;
static short sfifo[SFIFO_LEN];

static inline short sfifo_front()
{
	short s = 0;
	if(fifo_i != fifo_j)
	{
		s = sfifo[fifo_j];
		fifo_j = (fifo_j + 1) % SFIFO_LEN;
	}
	return s;
}

static inline void sfifo_push(short s)
{
	int idx = fifo_i;
	fifo_i = (fifo_i + 1) % SFIFO_LEN;
	if(fifo_i == fifo_j) fifo_j = (fifo_j + 1) % SFIFO_LEN;
	sfifo[idx] = s;
}


static void *send_loop(void *)
{
	bufitem_t sbuf[BUF_TAM];
	char dgbuf[BUF_TAM];
	
    const double K1 = (double)umb * xlen / (100.0 * xmlen * XM_GAP);
    const double K2 = (double)mute / (1000.0 * xlen);
    double Ex = XM0 * xlen;
    double xm_acum = 0.0;
	double Exm = (double)xmlen * XM0 * XM_GAP;
	double ExmK1 = Exm * K1;
	
	int l = 0, ll = 0;
	int j = delta, k = 0;
	xlen += delta;

	for(;;)
	{
		int r, n = 0;
		while(n < fsize)
		{
			if((r = read(fd_dsp, ((char*)sbuf) + n, fsize - n)) > 0)
			{
				n += r;
			}
			else if(errno == EAGAIN)
			{
				if (ndelay) usleep((fsize - n) * 20);
			}
			else
			{
				perror("send_loop: Reading from dsp");
				_exit(-1);
			}
		}
		
		if(mute)
		{
			for(int i = 0; i < FSIZE_LEN; i++)
			{
				double xn = use_fifo ? (double)sfifo_front() : (double)sbuf[i].r;
				double y = (b[0]*xn) + z[0];
				z[0] = (b[1]*xn) + z[1] - (a[1]*y);
				z[1] = (b[2]*xn) + z[2] - (a[2]*y);
				z[2] = (b[3]*xn) + z[3] - (a[3]*y);
				z[3] = (b[4]*xn) - (a[4]*y);
				
				Ex += (x[k] - x[j]);
				x[j] = fabs(y);
				xm_acum += x[j];
				j = (j + 1) % xlen; k = (k + 1) % xlen;
				if(++ll == XM_GAP)
				{
					double xm_am = Exm / xmlen;
					if(xm_acum > xm_am) xm_acum = xm_am + ((xm_acum - xm_am) / 17.0);
					Exm += (xm_acum - xm[l]);
					xm[l] = xm_acum; xm_acum = 0;
					l = (l + 1) % xmlen; ll = 0;
					ExmK1 = Exm * K1;
				}
				double muffle = ((double)Ex - ExmK1) * K2;
				short s = sbuf[i].l;
				if(muffle > 1.0) s = (short)lround((double)s / muffle);
				SHORT2ALAW(dgbuf[i], s);
			}
		}
		else
		{
			for(int i = 0; i < FSIZE_LEN; i++) SHORT2ALAW(dgbuf[i], sbuf[i].l);
		}
		if(sendto(fd_udp, dgbuf, FSIZE_LEN, 0, (struct sockaddr *)&remote, sizeof(remote)) != FSIZE_LEN)
		{
			perror("send_loop: Sending to udp socket");
			_exit(-1);
		}
	}
}

void usage(const char *name)
{
	fprintf(stderr, "usage: \t%s [-h <host>] [-l <local port>] [-r <remote port>]\n"
			"\t\t [-V] [-b] [-t] [-p <prio>] [-s <fragment size>] [-f <fragment num>]\n"
			"\t\t [-F] [-m <mute value>] [-u <umbral>] [-k <xlen>] [-K <xmlen>] [-d <delta>]\n\n", name);
	_exit(-1);
}

int main(int argc, char *argv[])
{
	VERSIONLIT_IN_MAIN;
	const char *host = 0, *file = 0;
	int remote_port = 0;
	int local_port = 29002;
	int channels = 2, format = AFMT_S16_LE, speed = 8000;
	int fnum = 0;
	int prio = 25;
	
	for (int i = 0; i < COUNTOF(x); i++) x[i] = XM0;
	for (int i = 0; i < COUNTOF(xm); i++) xm[i] = XM0 * XM_GAP;
	
	for(int i = 1; i < argc; i++)
	{
		if(argv[i][0] == '-')
		{
			switch(argv[i][1])
			{
			case 'l': if(!argv[++i]) usage(argv[0]); local_port = atoi(argv[i]); break;
			case 'r': if(!argv[++i]) usage(argv[0]); remote_port = atoi(argv[i]); break;
			case 'h': if(!argv[++i]) usage(argv[0]); host = argv[i]; break;
			case 'p': if(!argv[++i]) usage(argv[0]); prio = atoi(argv[i]); break;
			case 'V': verb = 1; break;
			case 't': trun = 0; break;
			case 'b': ndelay = 0; break;
			case 'm': if(!argv[++i]) usage(argv[0]); mute = atoi(argv[i]); break;
			case 'u': if(!argv[++i]) usage(argv[0]); umb = atoi(argv[i]); break;
			case 's': if(!argv[++i]) usage(argv[0]); fsize = atoi(argv[i]); break;
			case 'f': if(!argv[++i]) usage(argv[0]); fnum = atoi(argv[i]); break;
			case 'd': if(!argv[++i]) usage(argv[0]); delta = atoi(argv[i]); break;
			case 'k': if(!argv[++i]) usage(argv[0]); xlen = atoi(argv[i]); break;
			case 'K': if(!argv[++i]) usage(argv[0]); xmlen = atoi(argv[i]); break;
			case 'F': use_fifo = 1; break;
			default: usage(argv[0]);
			}
		}
	}
	if(!remote_port) remote_port = local_port;
	if(verb) printf("local port: %d, remote port: %d, remote host: %s\n", local_port, remote_port, host ? host : "-");
	
	int aux = BUF_IND_MAX;
	while(aux > 6)
	{
		if(fsize & (1 << aux)) { fsize = (1 << aux); break; }
		aux--;
	}
	if(aux == 6) { fsize = (BUF_TAM * sizeof(bufitem_t)); aux = BUF_IND_MAX; }
	if(!fnum) fnum = 64 * 1024 / fsize;
	if(verb) printf("Trying fragsize: %d (%d), fragnum: %d \n", fsize, aux, fnum);

	if((fd_dsp = open("/dev/dsp", O_RDWR | (ndelay ? O_NDELAY : 0))) == -1)		
	{
		perror("Opening /dev/dsp device");
		_exit(-1);
	}
	aux |= (fnum << 16);	//number of fragments
	ioctl (fd_dsp, SNDCTL_DSP_SETFRAGMENT, &aux);
	if(!(aux & 0x0800)) use_fifo = 1; // mute = 0;

	if (ioctl(fd_dsp, SNDCTL_DSP_SETFMT, &format) == -1)
	{
		perror("Ioctl SNDCTL_DSP_SETFMT");
		_exit(-1);
	}
	if (ioctl(fd_dsp, SNDCTL_DSP_CHANNELS, &channels) == -1)
	{
		perror("Ioctl SNDCTL_DSP_CHANNELS");
		_exit(-1);
	}
	if (ioctl(fd_dsp, SNDCTL_DSP_SPEED, &speed) == -1)
	{
		perror("Ioctl SNDCTL_DSP_SPEED");
		_exit(-1);
	}
	if(verb) printf("Format: %d, channels: %d, speed: %d\n", format, channels, speed);
	if(verb) printf("Trunc: %d, ndelay: %d, use_fifo: %d, prio: %d\n", trun, ndelay, use_fifo, prio);
	
	if(xmlen < 1 || xlen >= MAX_XM) xlen = 512;
	if(xlen < 1 || xlen >= MAX_X) xlen = 80;
	if(delta < 1 || (delta + xlen) > MAX_X) delta = 1;
	if(verb) printf("Mute: %d, umb: %d, xmlen: %d, xlen: %d, delta: %d\n", mute, umb, xmlen, xlen, delta);
	
	if((fd_udp = socket(PF_INET, SOCK_DGRAM, 0)) == -1)
	{
		perror("Requesting socket");
		_exit(-1);
	}
	struct sockaddr_in local = { 0 };
	local.sin_family = AF_INET;
	local.sin_port = htons(local_port);
	local.sin_addr.s_addr = INADDR_ANY;
	if(bind(fd_udp, (struct sockaddr *)&local, sizeof(local)) == -1)
	{
		fprintf(stderr, "Binding socket (port: %d)\n", local_port);
		perror("bind");
		_exit(-1);
	}
	
	char buffer[4096];

	if(host)
	{
		remote.sin_family = AF_INET;
		remote.sin_port = htons(remote_port);
		if(!inet_aton(host, &remote.sin_addr))
		{
			struct addrinfo *addr_info = NULL;
			struct addrinfo hints = { 0 };
			hints.ai_family = PF_INET;
			hints.ai_socktype = SOCK_STREAM;
			if(!getaddrinfo(host, NULL, &hints, &addr_info))
			{
				remote.sin_addr = ((struct sockaddr_in *)(addr_info->ai_addr))->sin_addr;
				freeaddrinfo(addr_info);
			}
			else
			{
				fprintf(stderr, "Incorrect host or error resolving: %s\n", host);
				_exit(-1);
			}
		}
	}
	else
	{
		socklen_t slen = sizeof(remote);
		if(recvfrom(fd_udp, buffer, sizeof(buffer), MSG_PEEK, (struct sockaddr *)&remote, &slen) <= 0)
		{
			perror("Receiving first datagram");
			_exit(-1);
		}
	}
	pthread_t tid; int r;
	if ((r = pthread_create(&tid, NULL, send_loop, NULL)) != 0)
	{
		fprintf(stderr, "Creating recv_loop thread (%d)\n", r);
		_exit(-1);
	}
	pthread_detach(tid);
#ifdef _ARM_LIT
	struct sched_param params;
	params.sched_priority = prio;
	if ((r = pthread_setschedparam(pthread_self(), SCHED_FIFO, &params)) != 0)
	{
		fprintf(stderr, "Couldn't set realtime prio for main thread (prio: %d) (%d)\n", prio, r);
	}
	params.sched_priority = prio - 1;
	if ((r = pthread_setschedparam(tid, SCHED_FIFO, &params)) != 0)
	{
		fprintf(stderr, "Couldn't set realtime prio for second thread (prio: %d) (%d)\n", prio - 1, r);
	}
	if (mlockall(MCL_FUTURE) == -1)
	{
		perror("Couldn't set mlockall(MCL_FUTURE)");
	}
#endif
	void *base = buffer;
	int offset = 0;
	struct iovec vbuf[64];
	bufitem_t sbuf[BUF_TAM];
	int vec_len = sizeof(buffer) / FSIZE_LEN;
	for(int i = 0; i < vec_len; i++)
	{
		vbuf[i].iov_base = buffer + (FSIZE_LEN * i);
		vbuf[i].iov_len = FSIZE_LEN;
	}
	for(;;)
	{
		if((r = readv(fd_udp, vbuf, vec_len)) <= 0) perror("readv"), _exit(-1);
		if(trun) while(recv(fd_udp, sbuf, BUF_TAM, MSG_DONTWAIT) > 0); //empty datagrams
		r += offset;
		vbuf[0].iov_base = base;
		int k = 0;
		while(r >= FSIZE_LEN)
		{
			for(int i = 0; i < FSIZE_LEN; i++)
			{
				ALAW2SHORT(sbuf[i].l, ((char*)(vbuf[k].iov_base))[i]);
				sbuf[i].r = sbuf[i].l;
				if(use_fifo) sfifo_push(sbuf[i].l);
			} 
			write(fd_dsp, sbuf, fsize);
			r -= FSIZE_LEN;
			k++;
		}
		if((offset = r))
		{
			vbuf[0].iov_len = FSIZE_LEN - offset;
			if(k)
			{
				vbuf[0].iov_base = vbuf[k].iov_base;
				vbuf[k].iov_len = FSIZE_LEN;
				vbuf[k].iov_base = base;
				base = vbuf[0].iov_base;
			}
			vbuf[0].iov_base = (char*)base + offset;
		}
		else
		{
			vbuf[0].iov_len = FSIZE_LEN;
		}
	}
}

