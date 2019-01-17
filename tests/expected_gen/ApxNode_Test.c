//////////////////////////////////////////////////////////////////////////////
// INCLUDES
//////////////////////////////////////////////////////////////////////////////
#include <string.h>
#include <stdio.h>
#include "ApxNode_Test.h"
#include "pack.h"

//////////////////////////////////////////////////////////////////////////////
// CONSTANTS AND DATA TYPES
//////////////////////////////////////////////////////////////////////////////
#define APX_DEFINITON_LEN 209u
#define APX_IN_PORT_DATA_LEN 7u
#define APX_OUT_PORT_DATA_LEN 12u
//////////////////////////////////////////////////////////////////////////////
// LOCAL FUNCTIONS
//////////////////////////////////////////////////////////////////////////////
static void outPortData_writeCmd(apx_offset_t offset, apx_size_t len );
//////////////////////////////////////////////////////////////////////////////
// LOCAL VARIABLES
//////////////////////////////////////////////////////////////////////////////
static const uint8_t m_outPortInitData[APX_OUT_PORT_DATA_LEN]= {
   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255
};

static uint8 m_outPortdata[APX_OUT_PORT_DATA_LEN];
static uint8_t m_outPortDirtyFlags[APX_OUT_PORT_DATA_LEN];
static const uint8_t m_inPortInitData[APX_IN_PORT_DATA_LEN]= {
   255, 255, 255, 255, 255, 255, 255
};

static uint8 m_inPortdata[APX_IN_PORT_DATA_LEN];
static uint8_t m_inPortDirtyFlags[APX_IN_PORT_DATA_LEN];
static apx_nodeData_t m_nodeData;
static const char *m_apxDefinitionData=
"APX/1.2\n"
"N\"Test\"\n"
"T\"SoundRequest_T\"{\"SoundId\"S\"Volume\"C}\n"
"P\"U16ARPort\"S[4]:={65535, 65535, 65535, 65535}\n"
"P\"U32Port\"L:=4294967295\n"
"R\"SoundRequest\"T[0]:={65535,255}\n"
"R\"U8ARPort\"C[3]:={255, 255, 255}\n"
"R\"U8Port\"C:=255\n"
"\n";

//////////////////////////////////////////////////////////////////////////////
// GLOBAL FUNCTIONS
//////////////////////////////////////////////////////////////////////////////
void ApxNode_Init_Test(void)
{
   memcpy(&m_inPortdata[0], &m_inPortInitData[0], APX_IN_PORT_DATA_LEN);
   memset(&m_inPortDirtyFlags[0], 0, sizeof(m_inPortDirtyFlags));
   memcpy(&m_outPortdata[0], &m_outPortInitData[0], APX_OUT_PORT_DATA_LEN);
   memset(&m_outPortDirtyFlags[0], 0, sizeof(m_outPortDirtyFlags));
   apx_nodeData_create(&m_nodeData, "Test", (uint8_t*) &m_apxDefinitionData[0], APX_DEFINITON_LEN, &m_inPortdata[0], &m_inPortDirtyFlags[0], APX_IN_PORT_DATA_LEN, &m_outPortdata[0], &m_outPortDirtyFlags[0], APX_OUT_PORT_DATA_LEN);
#ifdef APX_POLLED_DATA_MODE
   rbfs_create(&m_outPortDataCmdQueue, &m_outPortDataCmdBuf[0], APX_NUM_OUT_PORTS, APX_DATA_WRITE_CMD_SIZE);
#endif
}

apx_nodeData_t * ApxNode_GetNodeData_Test(void)
{
   return &m_nodeData;
}

Std_ReturnType ApxNode_Read_Test_SoundRequest(SoundRequest_T *val)
{
   uint8 *p;
   apx_nodeData_lockInPortData(&m_nodeData);
   p=&m_inPortdata[0];
   val->SoundId = (uint16) unpackLE(p,(uint8) sizeof(uint16));
   p+=(uint8) sizeof(uint16);
   val->Volume = (uint8) unpackLE(p,(uint8) sizeof(uint8));
   p+=(uint8) sizeof(uint8);
   apx_nodeData_unlockInPortData(&m_nodeData);
   return E_OK;
}

Std_ReturnType ApxNode_Read_Test_U8ARPort(uint8 *val)
{
   uint8 *p;
   uint8 i;
   apx_nodeData_lockInPortData(&m_nodeData);
   p=&m_inPortdata[3];
   for(i=0;i<3;i++)
   {
      val[i] = (uint8) unpackLE(p,(uint8) sizeof(uint8));
      p+=(uint8) sizeof(uint8);
   }
   apx_nodeData_unlockInPortData(&m_nodeData);
   return E_OK;
}

Std_ReturnType ApxNode_Read_Test_U8Port(uint8 *val)
{
   apx_nodeData_lockInPortData(&m_nodeData);
   *val = (uint8) m_inPortdata[6];
   apx_nodeData_unlockInPortData(&m_nodeData);
   return E_OK;
}

Std_ReturnType ApxNode_Write_Test_U16ARPort(uint16 *val)
{
   uint8 *p;
   uint8 i;
   apx_nodeData_lockOutPortData(&m_nodeData);
   p=&m_outPortdata[0];
   for(i=0;i<4;i++)
   {
      packLE(p,(uint32) val[i],(uint8) sizeof(uint16));
      p+=(uint8) sizeof(uint16);
   }
   outPortData_writeCmd(0, 8);
   return E_OK;
}

Std_ReturnType ApxNode_Write_Test_U32Port(uint32 val)
{
   apx_nodeData_lockOutPortData(&m_nodeData);
   packLE(&m_outPortdata[8],(uint32) val,(uint8) 4u);
   outPortData_writeCmd(8, 4);
   return E_OK;
}

void Test_inPortDataWritten(void *arg, apx_nodeData_t *nodeData, uint32_t offset, uint32_t len)
{
   (void)arg;
   (void)nodeData;
   (void)offset;
   (void)len;
}
//////////////////////////////////////////////////////////////////////////////
// LOCAL FUNCTIONS
//////////////////////////////////////////////////////////////////////////////
static void outPortData_writeCmd(apx_offset_t offset, apx_size_t len )
{
   if ( (m_outPortDirtyFlags[offset] == 0) && (true == apx_nodeData_isOutPortDataOpen(&m_nodeData) ) )
   {
      m_outPortDirtyFlags[offset] = (uint8_t) 1u;
      apx_nodeData_unlockOutPortData(&m_nodeData);
      apx_nodeData_outPortDataNotify(&m_nodeData, (uint32_t) offset, (uint32_t) len);
      return;
   }
   apx_nodeData_unlockOutPortData(&m_nodeData);
}
