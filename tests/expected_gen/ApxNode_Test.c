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
#define APX_DEFINITON_LEN 299u
#define APX_IN_PORT_DATA_LEN 17u
#define APX_OUT_PORT_DATA_LEN 14u
//////////////////////////////////////////////////////////////////////////////
// LOCAL FUNCTIONS
//////////////////////////////////////////////////////////////////////////////
static void outPortData_writeCmd(apx_offset_t offset, apx_size_t len );
//////////////////////////////////////////////////////////////////////////////
// LOCAL VARIABLES
//////////////////////////////////////////////////////////////////////////////
static const uint8_t m_outPortInitData[APX_OUT_PORT_DATA_LEN]= {
   1, 0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255
};

static uint8 m_outPortdata[APX_OUT_PORT_DATA_LEN];
static uint8_t m_outPortDirtyFlags[APX_OUT_PORT_DATA_LEN];
static const uint8_t m_inPortInitData[APX_IN_PORT_DATA_LEN]= {
   255, 127, 1, 0, 0, 0, 1, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255
};

static uint8 m_inPortdata[APX_IN_PORT_DATA_LEN];
static uint8_t m_inPortDirtyFlags[APX_IN_PORT_DATA_LEN];
static apx_nodeData_t m_nodeData;
static const char *m_apxDefinitionData=
"APX/1.2\n"
"N\"Test\"\n"
"T\"SoundRequest_T\"{\"SoundId\"S\"Volume\"C}\n"
"P\"PS8ARPort\"c[1]:={1}\n"
"P\"PS8Port\"c:=0\n"
"P\"PU16ARPort\"S[4]:={65535, 65535, 65535, 65535}\n"
"P\"PU32Port\"L:=4294967295\n"
"R\"RS16ARPort\"s[3]:={32767, 1, 0}\n"
"R\"RS32Port\"l:=1\n"
"R\"RU8ARPort\"C[3]:={255, 255, 255}\n"
"R\"RU8Port\"C:=255\n"
"R\"SoundRequest\"T[0]:={65535,255}\n"
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

Std_ReturnType ApxNode_Read_Test_RS16ARPort(sint16 *val)
{
   uint8 *p;
   uint8 i;
   apx_nodeData_lockInPortData(&m_nodeData);
   p=&m_inPortdata[0];
   for(i=0;i<3;i++)
   {
      val[i] = (sint16) unpackLE(p,(uint8) sizeof(sint16));
      p+=sizeof(sint16);
   }
   apx_nodeData_unlockInPortData(&m_nodeData);
   return E_OK;
}

Std_ReturnType ApxNode_Read_Test_RS32Port(sint32 *val)
{
   apx_nodeData_lockInPortData(&m_nodeData);
   *val = (sint32) unpackLE(&m_inPortdata[6],(uint8) sizeof(sint32));
   apx_nodeData_unlockInPortData(&m_nodeData);
   return E_OK;
}

Std_ReturnType ApxNode_Read_Test_RU8ARPort(uint8 *val)
{
   uint8 *p;
   uint8 i;
   apx_nodeData_lockInPortData(&m_nodeData);
   p=&m_inPortdata[10];
   for(i=0;i<3;i++)
   {
      val[i] = (uint8) *p;
      p++;
   }
   apx_nodeData_unlockInPortData(&m_nodeData);
   return E_OK;
}

Std_ReturnType ApxNode_Read_Test_RU8Port(uint8 *val)
{
   apx_nodeData_lockInPortData(&m_nodeData);
   *val = (uint8) m_inPortdata[13];
   apx_nodeData_unlockInPortData(&m_nodeData);
   return E_OK;
}

Std_ReturnType ApxNode_Read_Test_SoundRequest(SoundRequest_T *val)
{
   uint8 *p;
   apx_nodeData_lockInPortData(&m_nodeData);
   p=&m_inPortdata[14];
   val->SoundId = (uint16) unpackLE(p,(uint8) sizeof(uint16));
   p+=sizeof(uint16);
   val->Volume = (uint8) *p;
   p++;
   apx_nodeData_unlockInPortData(&m_nodeData);
   return E_OK;
}

Std_ReturnType ApxNode_Write_Test_PS8ARPort(sint8 *val)
{
   uint8 *p;
   uint8 i;
   apx_nodeData_lockOutPortData(&m_nodeData);
   p=&m_outPortdata[0];
   for(i=0;i<1;i++)
   {
      *p=(uint8) val[i];
      p++;
   }
   outPortData_writeCmd(0, 1);
   return E_OK;
}

Std_ReturnType ApxNode_Write_Test_PS8Port(sint8 val)
{
   apx_nodeData_lockOutPortData(&m_nodeData);
   m_outPortdata[1]=(unit8) val;
   outPortData_writeCmd(1, 1);
   return E_OK;
}

Std_ReturnType ApxNode_Write_Test_PU16ARPort(uint16 *val)
{
   uint8 *p;
   uint8 i;
   apx_nodeData_lockOutPortData(&m_nodeData);
   p=&m_outPortdata[2];
   for(i=0;i<4;i++)
   {
      packLE(p,(uint32) val[i],(uint8) sizeof(uint16));
      p+=sizeof(uint16);
   }
   outPortData_writeCmd(2, 8);
   return E_OK;
}

Std_ReturnType ApxNode_Write_Test_PU32Port(uint32 val)
{
   apx_nodeData_lockOutPortData(&m_nodeData);
   packLE(&m_outPortdata[10],(uint32) val,(uint8) sizeof(uint32));
   outPortData_writeCmd(10, 4);
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
