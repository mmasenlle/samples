/*******************************************************************************
 * Copyright (c) 2009, Rockwell Automation, Inc.
 * All rights reserved.
 *
 ******************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <pthread.h>
#include <unistd.h>

#include "generic_networkhandler.h"
#include "opener_api.h"
#include "cipcommon.h"
#include "trace.h"
#include "networkconfig.h"
#include "doublylinkedlist.h"
#include "cipconnectionobject.h"

extern int print_debug_;
/******************************************************************************/
/** @brief Signal handler function for ending stack execution
 *
 * @param signal the signal we received
 */
void LeaveStack(int signal);

/*****************************************************************************/
/** @brief Flag indicating if the stack should end its execution
 */
int g_end_stack = 0;

#define NO_MAIN

int serial_number = 123456789;
int set_serial_number(int sn) {
  if (sn > 0) serial_number = sn;
  return serial_number;
}

#ifdef NO_MAIN
extern int opener_loop(const char *nif);

int init_loop(const char *nif) {
pthread_t tid; int r, prio = 57;
    if (!nif) nif = "eth0";
	if ((r = pthread_create(&tid, NULL, opener_loop, nif)) != 0)
	{
		fprintf(stderr, "Creating opener_loop thread (%d)\n", r);
		return(-1);
	}
	pthread_detach(tid);

	struct sched_param params;
	params.sched_priority = prio;/*
	if ((r = pthread_setschedparam(pthread_self(), SCHED_FIFO, &params)) != 0)
	{
		fprintf(stderr, "Couldn't set realtime prio for main thread (prio: %d) (%d)\n", prio, r);
	}
	params.sched_priority = prio - 1; */
	if ((r = pthread_setschedparam(tid, SCHED_FIFO, &params)) != 0)
	{
		fprintf(stderr, "Couldn't set realtime prio for second thread (prio: %d) (%d)\n", prio - 1, r);
	}
/*
	if (mlockall(MCL_FUTURE) == -1)
	{
		perror("Couldn't set mlockall(MCL_FUTURE)");
	}
*/
return 0;
}

int opener_loop(const char *nif) {

EipUint16 unique_connection_id;

  OPENER_TRACE_STATE("Opener trace state\n");
  if (print_debug_) printf("OPENER_TRACE_LEVEL: %x\n", OPENER_TRACE_LEVEL);

    DoublyLinkedListInitialize(&connection_list,
                               CipConnectionObjectListArrayAllocator,
                               CipConnectionObjectListArrayFree);
    /* fetch Internet address info from the platform */
    if (kEipStatusError == ConfigureNetworkInterface(nif)) {
      printf("Network interface %s not found.\n", nif);
      exit(0);
    }
    ConfigureDomainName();
    ConfigureHostName();

    ConfigureMacAddress(nif);

#else
/******************************************************************************/
int main(int argc,
         char *arg[]) {

  EipUint16 unique_connection_id;

OPENER_TRACE_STATE("Opener trace state\n");
printf("OPENER_TRACE_LEVEL: %x\n", OPENER_TRACE_LEVEL);

  if (argc != 2) {
    printf("Wrong number of command line parameters!\n");
    printf("The correct command line parameters are:\n");
    printf("./OpENer interfacename\n");
    printf("    e.g. ./OpENer eth1\n");
    exit(0);
  } else {
    DoublyLinkedListInitialize(&connection_list,
                               CipConnectionObjectListArrayAllocator,
                               CipConnectionObjectListArrayFree);
    /* fetch Internet address info from the platform */
    if (kEipStatusError == ConfigureNetworkInterface(arg[1])) {
      printf("Network interface %s not found.\n", arg[1]);
      exit(0);
    }
    ConfigureDomainName();
    ConfigureHostName();

    ConfigureMacAddress(arg[1]);
  }
#endif

  /*for a real device the serial number should be unique per device */
  SetDeviceSerialNumber(serial_number);

  /* nUniqueConnectionID should be sufficiently random or incremented and stored
   *  in non-volatile memory each time the device boots.
   */
  unique_connection_id = rand();

  /* Setup the CIP Layer */
  CipStackInit(unique_connection_id);

  /* Setup Network Handles */
  if ( kEipStatusOk == NetworkHandlerInitialize() ) {
    g_end_stack = 0;
#ifndef WIN32
    /* register for closing signals so that we can trigger the stack to end */
    signal(SIGHUP, LeaveStack);
#endif

    /* The event loop. Put other processing you need done continually in here */
    while (1 != g_end_stack) {
      if ( kEipStatusOk != NetworkHandlerProcessOnce() ) {
        OPENER_TRACE_ERR("Error in NetworkHandler loop! Exiting OpENer!\n");
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

void LeaveStack(int signal) {
  (void) signal; /* kill unused parameter warning */
  OPENER_TRACE_STATE("got signal HUP\n");
  g_end_stack = 1;
}
