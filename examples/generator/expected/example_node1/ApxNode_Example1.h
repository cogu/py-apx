#ifndef APXNODE_EXAMPLE1_H
#define APXNODE_EXAMPLE1_H

#include <stdbool.h>
#include "apx_nodeData.h"
#include "Rte_Type.h"

//////////////////////////////////////////////////////////////////////////////
// CONSTANTS
//////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
// FUNCTION PROTOTYPES
//////////////////////////////////////////////////////////////////////////////
apx_nodeData_t * ApxNode_Init_Example1(void);
apx_nodeData_t * ApxNode_GetNodeData_Example1(void);
bool ApxNode_IsConnected_Example1(void);

Std_ReturnType ApxNode_Read_Example1_EngineRunningStatus(OffOn_T *val);
Std_ReturnType ApxNode_Read_Example1_VehicleSpeed(VehicleSpeed_T *val);
Std_ReturnType ApxNode_Write_Example1_FuelLevelPercent(Percent_T val);
void Example1_inPortDataWritten(void *arg, apx_nodeData_t *nodeData, uint32_t offset, uint32_t len);

#endif //APXNODE_EXAMPLE1_H
