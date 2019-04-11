#ifndef APXNODE_TESTCALLBACKLAST_H
#define APXNODE_TESTCALLBACKLAST_H

#include "apx_nodeData.h"

//////////////////////////////////////////////////////////////////////////////
// CONSTANTS
//////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
// FUNCTION PROTOTYPES
//////////////////////////////////////////////////////////////////////////////
void ApxNode_Init_TestCallbackLast(void);
apx_nodeData_t * ApxNode_GetNodeData_TestCallbackLast(void);

Std_ReturnType ApxNode_Read_TestCallbackLast_RS32Port(sint32 *val);
Std_ReturnType ApxNode_Read_TestCallbackLast_RU8Port(uint8 *val);
void TestCallbackLast_inPortDataWritten(void *arg, apx_nodeData_t *nodeData, uint32_t offset, uint32_t len);

#endif //APXNODE_TESTCALLBACKLAST_H
