#ifndef APXNODE_TESTSIMPLEONLYR_H
#define APXNODE_TESTSIMPLEONLYR_H

#include <stdbool.h>
#include "apx_nodeData.h"

//////////////////////////////////////////////////////////////////////////////
// CONSTANTS
//////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
// FUNCTION PROTOTYPES
//////////////////////////////////////////////////////////////////////////////
apx_nodeData_t * ApxNode_Init_TestSimpleOnlyR(void);
apx_nodeData_t * ApxNode_GetNodeData_TestSimpleOnlyR(void);
bool ApxNode_IsConnected_TestSimpleOnlyR(void);

Std_ReturnType ApxNode_Read_TestSimpleOnlyR_RU16Port(uint16 *val);
void TestSimpleOnlyR_inPortDataWritten(void *arg, apx_nodeData_t *nodeData, uint32_t offset, uint32_t len);

#endif //APXNODE_TESTSIMPLEONLYR_H
