#ifndef APXNODE_EXAMPLE2_H
#define APXNODE_EXAMPLE2_H

#include <stdbool.h>
#include "apx_nodeData.h"
#include "Rte_Type.h"

//////////////////////////////////////////////////////////////////////////////
// CONSTANTS
//////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
// FUNCTION PROTOTYPES
//////////////////////////////////////////////////////////////////////////////
apx_nodeData_t * ApxNode_Init_Example2(void);
apx_nodeData_t * ApxNode_GetNodeData_Example2(void);
bool ApxNode_IsConnected_Example2(void);

Std_ReturnType ApxNode_Read_Example2_EngineSpeed(EngineSpeed_T *val);
Std_ReturnType ApxNode_Read_Example2_FuelLevelPercent(Percent_T *val);
Std_ReturnType ApxNode_Read_Example2_Rtc_Seconds(Seconds_T *val);
Std_ReturnType ApxNode_Write_Example2_EngineRunningStatus(OffOn_T val);
Std_ReturnType ApxNode_Write_Example2_VehicleSpeed(VehicleSpeed_T val);
void Example2_inPortDataWritten(void *arg, apx_nodeData_t *nodeData, uint32_t offset, uint32_t len);

#endif //APXNODE_EXAMPLE2_H
