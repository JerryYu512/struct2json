from typing import Dict, List

int8_t = "int8_t"
uint8_t = "uint8_t"
int16_t = "int16_t"
uint16_t = "uint16_t"
int32_t = "int32_t"
uint32_t = "uint32_t"
int64_t = "int64_t"
uint64_t = "uint64_t"
float_t = "float_t"
double_t = "double_t"
boolean_t = "bool"
str_t = "std::string"
list_t = "list"
object_t = "object"

# 支持的类型
basic_inttypes = (int8_t, uint8_t, int16_t, uint16_t,
                  int32_t, uint32_t, int64_t, uint64_t, boolean_t, float_t, double_t, str_t)

inttypes = (int8_t, int16_t, int32_t, int64_t)
uinttypes = (uint8_t, uint16_t, uint32_t, uint64_t)
ftypes = (float_t, double_t)

# 类型的最大值
int8_max = "INT8_MAX"
uint8_max = "UINT8_MAX"
int16_max = "INT16_MAX"
uint16_max = "UINT16_MAX"
int32_max = "INT32_MAX"
uint32_max = "UINT32_MAX"
int64_max = "INT64_MAX"
uint64_max = "UINT64_MAX"
true = "true"
false = "false"


class SubType:
    def __init__(self, name, subtype):
        self.name = name
        self.type = subtype


class NodeAttr:
    def __init__(self, type: str, require: bool = True, default_value=None, subtype: SubType = None, desc: str = None,
                 range: str = None) -> None:
        self.type = type
        self.require = require
        if self.require:
            self.require = true
        else:
            self.require = false
        self.default_value = default_value
        if not self.default_value:
            if self.type in inttypes or self.type in uinttypes:
                self.default_value = "0"
            elif self.type in ftypes:
                self.default_value = "0.0"
            elif self.type == boolean_t:
                self.default_value = false
            elif self.type == str_t:
                self.default_value = ""

        self.subtype_name = str()
        self.subtype = None
        if subtype:
            self.subtype_name = subtype.name
            self.subtype = subtype.type
        self.desc = desc
