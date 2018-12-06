/*******************************************************************************
 * Copyright (c) 2009, Rockwell Automation, Inc.
 * All rights reserved.
 *
 ******************************************************************************/
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>

#include "cipcommon.h"
#include "generic_networkhandler.h"
#include "networkconfig.h"
#include "opener_api.h"
#include "trace.h"

#include "ciptcpipinterface.h"

extern int newfd;
extern int print_debug_;

/******************************************************************************/
/*!\brief Signal handler function for ending stack execution
 *
 * @param pa_nSig the signal we received
 */
void LeaveStack(int pa_nSig);

/*****************************************************************************/
/*! \brief Flag indicating if the stack should end its execution
 */
int g_end_stack = 0;

#define NO_MAIN

#ifdef NO_MAIN
int opener_loop(int nif);
DWORD WINAPI ThreadFunc(void* data) {
  DWORD dwThreadPri = GetThreadPriority(GetCurrentThread());
  printf(TEXT("Current thread priority is 0x%x\n"), dwThreadPri);
  if (!SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_TIME_CRITICAL)) {
    printf(TEXT("Failed to end background mode (%d)\n"), GetLastError());
  }
  dwThreadPri = GetThreadPriority(GetCurrentThread());
  printf(TEXT("Set thread priority is 0x%x\n"), dwThreadPri);
  opener_loop((int) data);
}	  


__declspec(dllexport) int init_loop(int nif) {
  HANDLE thread = CreateThread(NULL, 0, ThreadFunc, (void*)nif, 0, NULL);
}
int opener_loop(int nif) {
  EipUint16 nUniqueConnectionID;

  OPENER_TRACE_STATE("Opener trace state\n");
  if (print_debug_) printf("OPENER_TRACE_LEVEL: %x\n", OPENER_TRACE_LEVEL);

  DoublyLinkedListInitialize(&connection_list,
                             CipConnectionObjectListArrayAllocator,
                             CipConnectionObjectListArrayFree);
  /* fetch Internet address info from the platform */
  /* fetch Internet address info from the platform */
  ConfigureDomainName(nif);
  ConfigureHostName(nif);
  ConfigureIpMacAddress(nif);

#else

/******************************************************************************/
int main(int argc, char *arg[]) {
  EipUint16 nUniqueConnectionID;

  if (argc != 2) {
    printf("Wrong number of command line parameters!\n");
    printf("The correct command line parameters are:\n");
    printf("./OpENer index\n");
    printf("    e.g. ./OpENer index\n");
    exit(0);
  } else {
    DoublyLinkedListInitialize(&connection_list,
                               CipConnectionObjectListArrayAllocator,
                               CipConnectionObjectListArrayFree);
    /* fetch Internet address info from the platform */
    ConfigureDomainName(atoi(arg[1]));
    ConfigureHostName(atoi(arg[1]));
    ConfigureIpMacAddress(atoi(arg[1]));

  }
#endif

  /*for a real device the serial number should be unique per device */
  SetDeviceSerialNumber(123456789);

  /* nUniqueConnectionID should be sufficiently random or incremented and stored
   *  in non-volatile memory each time the device boots.
   */
  nUniqueConnectionID = rand();

  /* Setup the CIP Layer */
  CipStackInit(nUniqueConnectionID);

  /* Setup Network Handles */
  if (kEipStatusOk == NetworkHandlerInitialize()) {
    int cnt = 0;
    g_end_stack = 0;
#ifndef WIN32
    /* register for closing signals so that we can trigger the stack to end */
    signal(SIGHUP, LeaveStack);
#endif

	if (print_debug_) {
        printf("*** domain_name.length: %d\n",
			   interface_configuration_.domain_name.length);
		printf("*** domain_name.string: %*.*s\n", 0,
			   interface_configuration_.domain_name.length,
			   interface_configuration_.domain_name.string);
		printf("*** host_name: 0x%08x\n", interface_configuration_.name_server);
		printf("*** ip_address: 0x%08x   ", interface_configuration_.ip_address);
		{
		  unsigned char bytes[4];
		  int ip = interface_configuration_.ip_address;
		  bytes[0] = ip & 0xFF;
		  bytes[1] = (ip >> 8) & 0xFF;
		  bytes[2] = (ip >> 16) & 0xFF;
		  bytes[3] = (ip >> 24) & 0xFF;
		  printf("%d.%d.%d.%d\n", bytes[0], bytes[1], bytes[2], bytes[3]);
		}
	}
    /* The event loop. Put other processing you need done continually in here */
    while (1 != g_end_stack) {
      int res = NetworkHandlerProcessOnce();
      // printf("***** NetworkHandlerProcessOnce(): 0x%x,   %d\n", res, cnt++);
      if (kEipStatusOk != res) {
        break;
      }
    }

    /* clean up network state */
    NetworkHandlerFinish();
  }
  /* close remaining sessions and connections, cleanup used data */
  ShutdownCipStack();

  return -1;
}

void LeaveStack(int pa_nSig) {
  (void)pa_nSig; /* kill unused parameter warning */
  OPENER_TRACE_STATE("got signal HUP\n");
  g_end_stack = 1;
}
