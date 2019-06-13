#ifndef APXNODE_TESTSIMPLE_H
#define APXNODE_TESTSIMPLE_H

#include <stdbool.h>
#include "apx_nodeData.h"

//////////////////////////////////////////////////////////////////////////////
// CONSTANTS
//////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
// FUNCTION PROTOTYPES
//////////////////////////////////////////////////////////////////////////////
apx_nodeData_t * ApxNode_Init_TestSimple(void);
apx_nodeData_t * ApxNode_GetNodeData_TestSimple(void);
bool ApxNode_IsConnected_TestSimple(void);

Std_ReturnType ApxNode_Read_TestSimple_RS32Port(sint32 *val);
Std_ReturnType ApxNode_Read_TestSimple_RU8Port(uint8 *val);
Std_ReturnType ApxNode_Write_TestSimple_PS8Port(sint8 val);
Std_ReturnType ApxNode_Write_TestSimple_PU32Port(uint32 val);
void TestSimple_inPortDataWritten(void *arg, apx_nodeData_t *nodeData, uint32_t offset, uint32_t len);

#endif //APXNODE_TESTSIMPLE_H
