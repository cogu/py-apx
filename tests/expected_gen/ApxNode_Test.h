#ifndef APXNODE_TEST_H
#define APXNODE_TEST_H

#include "apx_nodeData.h"

//////////////////////////////////////////////////////////////////////////////
// CONSTANTS
//////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
// FUNCTION PROTOTYPES
//////////////////////////////////////////////////////////////////////////////
void ApxNode_Init_Test(void);
apx_nodeData_t * ApxNode_GetNodeData_Test(void);

Std_ReturnType ApxNode_Read_Test_SoundRequest(SoundRequest_T *val);
Std_ReturnType ApxNode_Read_Test_U8ARPort(uint8 *val);
Std_ReturnType ApxNode_Read_Test_U8Port(uint8 *val);
Std_ReturnType ApxNode_Write_Test_U16ARPort(uint16 *val);
Std_ReturnType ApxNode_Write_Test_U32Port(uint32 val);
void Test_inPortDataWritten(void *arg, apx_nodeData_t *nodeData, uint32_t offset, uint32_t len);

#endif //APXNODE_TEST_H
