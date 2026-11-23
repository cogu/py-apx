#ifndef APXNODE_EXAMPLE3_H
#define APXNODE_EXAMPLE3_H

#include <stdbool.h>
#include "apx_nodeData.h"
#include "CustomTypes.h"

//////////////////////////////////////////////////////////////////////////////
// CONSTANTS
//////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
// FUNCTION PROTOTYPES
//////////////////////////////////////////////////////////////////////////////
apx_nodeData_t * ApxNode_Init_Example3(void);
apx_nodeData_t * ApxNode_GetNodeData_Example3(void);
bool ApxNode_IsConnected_Example3(void);

Std_ReturnType ApxNode_Read_Example3_EngineSpeed(EngineSpeed_T *val);
Std_ReturnType ApxNode_Read_Example3_FuelLevelPercent(Percent_T *val);
Std_ReturnType ApxNode_Read_Example3_Rtc_Seconds(Seconds_T *val);
Std_ReturnType ApxNode_Write_Example3_EngineRunningStatus(OffOn_T val);
Std_ReturnType ApxNode_Write_Example3_VehicleSpeed(VehicleSpeed_T val);
void Example3_inPortDataWritten(void *arg, apx_nodeData_t *nodeData, uint32_t offset, uint32_t len);

#endif //APXNODE_EXAMPLE3_H
