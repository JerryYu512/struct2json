from typing import List, Dict, Tuple

int8_t = "int8_t"
uint8_t = "uint8_t"
int16_t = "int16_t"
uint16_t = "uint16_t"
int32_t = "int32_t"
uint32_t = "uint32_t"
int64_t = "int64_t"
uint64_t = "uint64_t"

# 支持的类型
inttypes = (int8_t, uint8_t, int16_t, uint16_t,
            int32_t, uint32_t, int64_t, uint64_t)

# 类型的最大值
int8_max = "INT8_MAX"
uint8_max = "UINT8_MAX"
int16_max = "INT16_MAX"
uint16_max = "UINT16_MAX"
int32_max = "INT32_MAX"
uint32_max = "UINT32_MAX"
int64_max = "INT64_MAX"
uint64_max = "UINT64_MAX"


class EnumNode:
    def __init__(self, name: str, value: str = None, string: str = None, desc: str = None) -> None:
        """初始化

        Args:
            name (str): 枚举名称
            value (str, optional): 枚举值，字符串格式，可传入2/8/10/16进制，以及常量算术运算. Defaults to None.
            string (str, optional): 枚举对应的自定义字符串映射. Defaults to None.
            desc (str, optional): 描述，用于注释. Defaults to None.
        """
        self.name = name
        self.value = value
        self.string = string
        self.desc = desc


class EnumDef:
    def __init__(self, name: str, etype: str, desc: str = None, enums: List[EnumNode] = None) -> None:
        """枚举定义

        Args:
            name (str): 枚举类型名
            etype (str): 枚举对应的类型
            desc (str, optional): 描述，用于注释. Defaults to None.
            enums (List[EnumNode], optional): 枚举成员列表
        """
        self.name = name
        self.etype = etype
        self.desc = desc
        self.enums = enums


def bit(off: int) -> str:
    """用于位移

    Args:
        off (int): 位移位置

    Returns:
        _type_: 字符串格式
    """
    return f'1 << {off}'


EnumDefs: List[EnumDef] = [
    EnumDef("AppMode", uint32_t, "可选运行模式", [
        EnumNode("APP_DEVICE_MODE", str(0), desc="设备模式"),
        EnumNode("APP_GATEWAY_MODE", bit(0), desc="设备模式"),
        EnumNode("APP_DEV_GW_MODE", bit(1), desc="设备模式"),
        EnumNode("APP_DEV_INVALID_MODE", uint32_max, desc="设备模式"),
    ]),
    EnumDef("DevMode", uint8_t, "可选运行模式", [
        EnumNode("DEV_DEVICE_MODE", str(0), "mode-1", desc="设备模式"),
        EnumNode("DEV_GATEWAY_MODE", bit(0), "mode-2", desc="设备模式"),
        EnumNode("DEV_DEV_GW_MODE", bit(1), "mode-3", desc="设备模式"),
        EnumNode("DEV_DEV_UNKNOWN_MODE", hex(0x81), "mode-3", desc="设备模式"),
        EnumNode("DEV_DEV_INVALID_MODE", int8_max, "mode-4", desc="设备模式"),
    ]),
]
