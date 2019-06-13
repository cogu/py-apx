#ifndef APXNODE_TESTCALLBACKFIRST_H
#define APXNODE_TESTCALLBACKFIRST_H

#include <stdbool.h>
#include "apx_nodeData.h"

//////////////////////////////////////////////////////////////////////////////
// CONSTANTS
//////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
// FUNCTION PROTOTYPES
//////////////////////////////////////////////////////////////////////////////
apx_nodeData_t * ApxNode_Init_TestCallbackFirst(void);
apx_nodeData_t * ApxNode_GetNodeData_TestCallbackFirst(void);
bool ApxNode_IsConnected_TestCallbackFirst(void);

Std_ReturnType ApxNode_Read_TestCallbackFirst_RS32Port(sint32 *val);
Std_ReturnType ApxNode_Read_TestCallbackFirst_RU8Port(uint8 *val);
void TestCallbackFirst_inPortDataWritten(void *arg, apx_nodeData_t *nodeData, uint32_t offset, uint32_t len);

#endif //APXNODE_TESTCALLBACKFIRST_H
