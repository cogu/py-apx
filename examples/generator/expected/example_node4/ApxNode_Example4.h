#ifndef APXNODE_EXAMPLE4_H
#define APXNODE_EXAMPLE4_H

#include <stdbool.h>
#include "apx_nodeData.h"
#include "Rte_Type.h"

//////////////////////////////////////////////////////////////////////////////
// CONSTANTS
//////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
// FUNCTION PROTOTYPES
//////////////////////////////////////////////////////////////////////////////
apx_nodeData_t * ApxNode_Init_Example4(void);
apx_nodeData_t * ApxNode_GetNodeData_Example4(void);
bool ApxNode_IsConnected_Example4(void);

Std_ReturnType ApxNode_Read_Example4_RecordReceiver(MyRecord_T *val);
Std_ReturnType ApxNode_Read_Example4_U16ArrayReceiver(uint16 *val);
Std_ReturnType ApxNode_Write_Example4_U16ArraySender(uint16 *val);
void Example4_inPortDataWritten(void *arg, apx_nodeData_t *nodeData, uint32_t offset, uint32_t len);

#endif //APXNODE_EXAMPLE4_H
