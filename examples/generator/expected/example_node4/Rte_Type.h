#ifndef RTE_TYPE_H
#define RTE_TYPE_H

/*********************************************************************************************************************
* Includes
*********************************************************************************************************************/
#include "Std_Types.h"

/*********************************************************************************************************************
* Data Type Definitions
*********************************************************************************************************************/

#define Rte_TypeDef_UInt16
typedef uint16 UInt16;
#define UInt16_LowerLimit ((UInt16)0u)
#define UInt16_UpperLimit ((UInt16)65535u)

#define Rte_TypeDef_UInt8
typedef uint8 UInt8;
#define UInt8_LowerLimit ((UInt8)0u)
#define UInt8_UpperLimit ((UInt8)255u)

#define Rte_TypeDef_U16Array_T
typedef UInt16 U16Array_T[4];

#define Rte_TypeDef_MyRecord_T
typedef struct
{
   UInt8 First;
   U16Array_T Second;
} MyRecord_T;


#ifndef RTE_SUPPRESS_UNUSED_DATATYPES

typedef boolean Boolean;

typedef sint16 SInt16;
#define SInt16_LowerLimit ((SInt16)-32768)
#define SInt16_UpperLimit ((SInt16)32767)

typedef sint32 SInt32;
#define SInt32_LowerLimit ((SInt32)-2147483648)
#define SInt32_UpperLimit ((SInt32)2147483647)

typedef sint8 SInt8;
#define SInt8_LowerLimit ((SInt8)-128)
#define SInt8_UpperLimit ((SInt8)127)

typedef uint32 UInt32;
#define UInt32_LowerLimit ((UInt32)0u)
#define UInt32_UpperLimit ((UInt32)4294967295u)

#endif

#endif //RTE_TYPE_H

