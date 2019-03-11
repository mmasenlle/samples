/*******************************************************************************
 * Copyright (c) 2012, Rockwell Automation, Inc.
 * All rights reserved.
 *
 ******************************************************************************/

#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

#include "opener_api.h"
#include "appcontype.h"

#define DEMO_APP_INPUT_ASSEMBLY_NUM                129 //100 //0x064
#define DEMO_APP_OUTPUT_ASSEMBLY_NUM               130 //150 //0x096
#define DEMO_APP_CONFIG_ASSEMBLY_NUM               128 //151 //0x097
#define DEMO_APP_HEARTBEAT_INPUT_ONLY_ASSEMBLY_NUM  152 //0x098
#define DEMO_APP_HEARTBEAT_LISTEN_ONLY_ASSEMBLY_NUM 153 //0x099
#define DEMO_APP_EXPLICT_ASSEMBLY_NUM              154 //0x09A

/* global variables for demo application (4 assembly data fields)  ************/

extern CipUint g_encapsulation_inactivity_timeout;

EipUint8 g_assembly_data064[32]; /* Input */
EipUint8 g_assembly_data096[32]; /* Output */
EipUint8 g_assembly_data097[10]; /* Config */
EipUint8 g_assembly_data09A[32]; /* Explicit */


EipUint8 g_assembly_config_data[256];
EipUint8 g_assembly_input_data[1024];  
EipUint8 g_assembly_output_data[1024]; 

static void *assembly_config_data_ptr = g_assembly_config_data;
static void *assembly_input_data_ptr = g_assembly_input_data; /* Input inteline */
static void *assembly_output_data_ptr = g_assembly_output_data;

static int assembly_config_instance = 128;
static int assembly_input_instance = 129;
static int assembly_output_instance = 130;
static int assembly_config_size = 10;
static int assembly_input_size = 4;
static int assembly_output_size = 396;

void set_data_config_ptr(void *ptr) {
  assembly_config_data_ptr = ptr;
}
void set_data_input_ptr(void *ptr) {
  assembly_input_data_ptr = ptr;
}
void set_data_output_ptr(void *ptr) {
  assembly_output_data_ptr = ptr;
}
EipUint8 *get_data_input() {
  return assembly_input_data_ptr;
}
EipUint8 *get_data_output() {
  return assembly_output_data_ptr;
}
void config_assemblies(int ci,int cs, int ii, int is, int oi, int os) {
  if (ci > 0) assembly_config_instance = ci;
  if (cs > 0) assembly_config_size = cs;
  if (ii > 0) assembly_input_instance = ii;
  if (is > 0) assembly_input_size = is;
  if (oi > 0) assembly_output_instance = oi;
  if (os > 0) assembly_output_size = os;
}
int print_debug_ = 1;
void set_print_debug(int v) { print_debug_ = v; }

EipStatus ApplicationInitialization(void) {

	memset(g_assembly_config_data, 0, sizeof(g_assembly_config_data));
	memset(g_assembly_input_data, 0, sizeof(g_assembly_input_data));
    memset(g_assembly_output_data, 0, sizeof(g_assembly_output_data));
	
  CreateAssemblyObject(assembly_config_instance, assembly_config_data_ptr,
                       assembly_config_size);
	    CreateAssemblyObject(assembly_input_instance, assembly_input_data_ptr,
                         assembly_input_size);
  CreateAssemblyObject(assembly_output_instance, assembly_output_data_ptr,
                       assembly_output_size);


  /*Heart-beat output assembly for Input only connections */
  CreateAssemblyObject(DEMO_APP_HEARTBEAT_INPUT_ONLY_ASSEMBLY_NUM, NULL, 0);

  /*Heart-beat output assembly for Listen only connections */
  CreateAssemblyObject(DEMO_APP_HEARTBEAT_LISTEN_ONLY_ASSEMBLY_NUM, NULL, 0);

  /* assembly for explicit messaging */
  CreateAssemblyObject( DEMO_APP_EXPLICT_ASSEMBLY_NUM, g_assembly_data09A,
                        sizeof(g_assembly_data09A) );
#if 0
  ConfigureExclusiveOwnerConnectionPoint(0, DEMO_APP_OUTPUT_ASSEMBLY_NUM,
                                         DEMO_APP_INPUT_ASSEMBLY_NUM,
                                         DEMO_APP_CONFIG_ASSEMBLY_NUM);
  ConfigureInputOnlyConnectionPoint(0,
                                    DEMO_APP_HEARTBEAT_INPUT_ONLY_ASSEMBLY_NUM,
                                    DEMO_APP_INPUT_ASSEMBLY_NUM,
                                    DEMO_APP_CONFIG_ASSEMBLY_NUM);
  ConfigureListenOnlyConnectionPoint(0,
                                     DEMO_APP_HEARTBEAT_LISTEN_ONLY_ASSEMBLY_NUM,
                                     DEMO_APP_INPUT_ASSEMBLY_NUM,
                                     DEMO_APP_CONFIG_ASSEMBLY_NUM);
#else
  ConfigureExclusiveOwnerConnectionPoint(0, assembly_output_instance,
                                         assembly_input_instance,
                                         assembly_config_instance);
  ConfigureInputOnlyConnectionPoint(
      0, DEMO_APP_HEARTBEAT_INPUT_ONLY_ASSEMBLY_NUM, assembly_input_instance,
      assembly_config_instance);
  ConfigureListenOnlyConnectionPoint(
      0, DEMO_APP_HEARTBEAT_LISTEN_ONLY_ASSEMBLY_NUM, assembly_input_instance,
      assembly_config_instance);
#endif
  return kEipStatusOk;
}

void HandleApplication(void) {
  /* check if application needs to trigger an connection */
}

void CheckIoConnectionEvent(unsigned int output_assembly_id,
                            unsigned int input_assembly_id,
                            IoConnectionEvent io_connection_event) {
  /* maintain a correct output state according to the connection state*/

  (void) output_assembly_id; /* suppress compiler warning */
  (void) input_assembly_id; /* suppress compiler warning */
  (void) io_connection_event; /* suppress compiler warning */
}

EipStatus AfterAssemblyDataReceived(CipInstance *instance) {
  EipStatus status = kEipStatusOk;

  if (print_debug_)
    printf("AfterAssemblyDataReceived(%d)\n", instance->instance_number);

  /*handle the data received e.g., update outputs of the device */
  switch (instance->instance_number) {
    case DEMO_APP_OUTPUT_ASSEMBLY_NUM:
      /* Data for the output assembly has been received.
       * Mirror it to the inputs
      memcpy( &g_assembly_data064[0], &g_assembly_data096[0],
              sizeof(g_assembly_data064) );
		 */
      break;
    case DEMO_APP_EXPLICT_ASSEMBLY_NUM:
      /* do something interesting with the new data from
       * the explicit set-data-attribute message */
      break;
    case DEMO_APP_CONFIG_ASSEMBLY_NUM:
      /* Add here code to handle configuration data and check if it is ok
       * The demo application does not handle config data.
       * However in order to pass the test we accept any data given.
       * EIP_ERROR
       */
      status = kEipStatusOk;
      break;
  }
  return status;
}

EipBool8 BeforeAssemblyDataSend(CipInstance *pa_pstInstance) {
  /*update data to be sent e.g., read inputs of the device */
  /*In this sample app we mirror the data from out to inputs on data receive
   * therefore we need nothing to do here. Just return true to inform that
   * the data is new.
   */

	if (print_debug_)
		printf("BeforeAssemblyDataSend(%d)\n", pa_pstInstance->instance_number);

  if (pa_pstInstance->instance_number == DEMO_APP_EXPLICT_ASSEMBLY_NUM) {
    /* do something interesting with the existing data
     * for the explicit get-data-attribute message */
  }
  return true;
}

EipStatus ResetDevice(void) {
  /* add reset code here*/
  CloseAllConnections();
  return kEipStatusOk;
}

EipStatus ResetDeviceToInitialConfiguration(void) {
  /*rest the parameters */
  g_encapsulation_inactivity_timeout = 120;
  /*than perform device reset*/
  ResetDevice();
  return kEipStatusOk;
}

void *
CipCalloc(size_t number_of_elements,
          size_t size_of_element) {
  return calloc(number_of_elements, size_of_element);
}

void CipFree(void *data) {
  free(data);
}

void RunIdleChanged(EipUint32 run_idle_value) {
  (void) run_idle_value;
}

