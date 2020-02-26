#ifndef APXNODE_TEST_COMPACT_H
#define APXNODE_TEST_COMPACT_H

#include <stdbool.h>
#include "apx_nodeData.h"

//////////////////////////////////////////////////////////////////////////////
// CONSTANTS
//////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
// FUNCTION PROTOTYPES
//////////////////////////////////////////////////////////////////////////////
apx_nodeData_t * ApxNode_Init_Test_compact(void);
apx_nodeData_t * ApxNode_GetNodeData_Test_compact(void);
bool ApxNode_IsConnected_Test_compact(void);

Std_ReturnType ApxNode_Read_Test_compact_RU8FirstPort(uint8 *val);
Std_ReturnType ApxNode_Read_Test_compact_RS16ARPort(sint16 *val);
Std_ReturnType ApxNode_Read_Test_compact_RS32Port(sint32 *val);
Std_ReturnType ApxNode_Read_Test_compact_RU8Port(uint8 *val);
Std_ReturnType ApxNode_Read_Test_compact_RU8ARPort(uint8 *val);
Std_ReturnType ApxNode_Read_Test_compact_LightRequest(LightRequest_T *val);
Std_ReturnType ApxNode_Read_Test_compact_SoundRequest(SoundRequest_T *val);
Std_ReturnType ApxNode_Read_Test_compact_RU8LastPort(uint8 *val);
Std_ReturnType ApxNode_Write_Test_compact_SoundRequestAck(SoundRequest_T *val);
Std_ReturnType ApxNode_Write_Test_compact_HapticRequest(HapticRequest_T *val);
Std_ReturnType ApxNode_Write_Test_compact_PS8ARPort(sint8 *val);
Std_ReturnType ApxNode_Write_Test_compact_PS8Port(sint8 val);
Std_ReturnType ApxNode_Write_Test_compact_PU16ARPort(uint16 *val);
Std_ReturnType ApxNode_Write_Test_compact_PU32Port(uint32 val);
void Test_compact_inPortDataWritten(void *arg, apx_nodeData_t *nodeData, uint32_t offset, uint32_t len);

#endif //APXNODE_TEST_COMPACT_H
