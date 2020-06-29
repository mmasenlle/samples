#include "stdafx.h"
#include <windows.h>
#include <stdio.h>
#include <string.h>

#include "TcAdsDef.h"
#include "TcAdsApi.h"
static AmsAddr Addr;
int ads_connect()
{
	long nErr, nPort;
	nPort = AdsPortOpen();
	nErr = AdsGetLocalAddress(&Addr);
	if (nErr) {
		fprintf(stderr, "Error: AdsGetLocalAddress: %d\n", nErr);
	}
	Addr.port = 851;
	return nErr;
}
int ads_write_f(const char *vname, float value)
{
	unsigned long lHdlVar;
	long nErr = AdsSyncReadWriteReq(&Addr, ADSIGRP_SYM_HNDBYNAME, 0x0, sizeof(lHdlVar), &lHdlVar,
		strlen(vname), (void*)vname);
	if (nErr) {
		fprintf(stderr, "Error: AdsSyncReadWriteReq(%s): %d\n", vname, nErr);
	}
	else {
		nErr = AdsSyncWriteReq(&Addr, ADSIGRP_SYM_VALBYHND, lHdlVar, sizeof(value), &value);
		if (nErr) {
			fprintf(stderr, "Error: AdsSyncWriteReq(%s, %f): %d\n", vname, value, nErr);
		}
	}
	return nErr;
}

static unsigned long _lHdlVar = 0;
static unsigned long _len = 0;
static void *_data_addr = 0;

int ads_init(const char *var_name, void *data_addr, unsigned long len)
{
	unsigned long lHdlVar;
	long nErr = ads_connect();
	if (nErr) return nErr;
	nErr = AdsSyncReadWriteReq(&Addr, ADSIGRP_SYM_HNDBYNAME, 0x0, sizeof(lHdlVar), &lHdlVar,
		strlen(var_name), (void*)var_name);
	if (nErr) {
		fprintf(stderr, "ads_init()->Error: AdsSyncReadWriteReq(%s): %d\n", var_name, nErr);
		return nErr;
	}
	_lHdlVar = lHdlVar;
	_len = len;
	_data_addr = data_addr;
	return 0;
}
int ads_write()
{
	if (_lHdlVar) {
		long nErr = AdsSyncWriteReq(&Addr, ADSIGRP_SYM_VALBYHND, _lHdlVar, _len, _data_addr);
		if (nErr) {
			fprintf(stderr, "ads_write()->Error: AdsSyncWriteReq(): %d\n", nErr);
		}
		return nErr;
	}
	return -1;
}