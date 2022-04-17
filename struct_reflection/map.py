from ds_define import *
from typing import Dict, List, Tuple

ITEM_STRUCT_NAME = "AppCfgParamSet"
STRUCT_DEFINE_FILENAME = "param_def.h"
STRUCT_TO_JSON_FILENAME = "param_struct2json"
JSON_TO_STRUCT_FILENAME = "param_json2struct"
namespace = "biot"


def sub(name: str) -> SubType:
    return SubType(name, eval(name))


AppCfgParamProduct: Dict[str, NodeAttr] = {

    "uuid": NodeAttr(str_t, True, desc="[rw,ro]配置参数文件唯一标识"),
}

AppCfgParamModule: Dict[str, NodeAttr] = {

    "uuid": NodeAttr(str_t, True, desc="[rw,ro]配置参数文件唯一标识"),
}

AppCfgParamSystem: Dict[str, NodeAttr] = {

    "uuid": NodeAttr(str_t, True, desc="[rw,ro]配置参数文件唯一标识"),
}

AppCfgParamBasic: Dict[str, NodeAttr] = {

    "uuid": NodeAttr(str_t, True, desc="[rw,ro]配置参数文件唯一标识"),
    "module": NodeAttr(object_t, True, subtype=sub("AppCfgParamModule"), desc="模块参数"),
}

AppCfgParamSet: Dict[str, NodeAttr] = {
    "uuid": NodeAttr(str_t, True, desc="[rw,ro]配置参数文件唯一标识"),
    "exec_id": NodeAttr(str_t, True, desc="[rw,ro]程序id"),
    "version": NodeAttr(uint32_t, True, "0", desc="[rw,ro]配置参数版本号"),
    "device_name": NodeAttr(str_t, True, "biot 01", desc="[rw,rw]设备名称"),
    "device_id": NodeAttr(str_t, True, "1", desc="[rw,rw]设备编号"),
    "basic": NodeAttr(object_t, True, subtype=sub("AppCfgParamBasic"), desc="基础功能参数"),
    "system": NodeAttr(object_t, True, subtype=sub("AppCfgParamSystem"), desc="系统参数"),
    "module": NodeAttr(object_t, True, subtype=sub("AppCfgParamModule"), desc="模块参数"),
    "product": NodeAttr(object_t, True, subtype=sub("AppCfgParamProduct"), desc="产品参数"),
    "product_l": NodeAttr(list_t, True, subtype=sub("AppCfgParamProduct"), desc="产品参数"),
}
