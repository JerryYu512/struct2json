from typing import Dict
from map import *
from string import Template

global_struct_def: List[Dict[str, str]] = list()
global_json2struct_code: List[Dict[str, Dict[str, str]]] = list()
global_struct2json_code: List[Dict[str, Dict[str, str]]] = list()
global_ns = str()

json2struct_template = """
template <typename T>
bool json2struct(simdjson::dom::element &js, T &st) {
    return false;
}
"""

struct2json_template = """
template <typename T>
bool struct2json(const T &st, nlohmann::json &js) {
    return false;
}
"""

convert_nor_tp = Template("""\t{ js["${key}"] = st.${key}; }""")

convert_object_tp = Template("""\t{ nlohmann::json node; struct2json(st.${key}, node); js["${key}"] = node; }""")

convert_list_nor_tp = Template("""\t{ for (auto &value: st.${key}) { js["${key}"].push_back(value); } }""")

convert_list_object_tp = Template("""\t{ for (auto &value: st.${key}) { nlohmann::json node; struct2json(value, node); js["${key}"].push_back(node); } }""")

get_bool_value_tp = Template("""\t{
\t\tbool val = false;
\t\tif (simdjson::SUCCESS != js["${key}"].get(val) || !js["${key}"].is_bool()) {
\t\t\tif (${required}) { std::cerr << "not find [${key}]" << std::endl; }
\t\t\ttst.${key} = ${default_value};
\t\t} else { tst.${key} = val; }
\t}
""")

get_int_value_tp = Template("""\t{
\t\t${full_type} val = 0;
\t\tif (simdjson::SUCCESS != js["${key}"].get(val) || !js["${key}"].is_number()) {
\t\t\tif (${required}) { std::cerr << "not find [${key}]" << std::endl; }
\t\t\t\ttst.${key} = ${default_value};
\t\t\t} else { tst.${key} = static_cast<${type}>(val);
\t\t}
\t}
""")

get_str_value_tp = Template("""\t{
\t\tconst char* val = nullptr;
\t\tif (simdjson::SUCCESS != js["${key}"].get(val) || !js["${key}"].is_string() || !val) {
\t\t\tif (${required}) { std::cerr << "not find [${key}]" << std::endl; }
\t\t\tconst char* d = "${default_value}";
\t\t\tif (d) { tst.${key} = d; }
\t\t} else { tst.${key} = val; }
\t}
""")

get_list_bool_value_tp = Template("""\t{
\t\tsimdjson::dom::array array;
\t\tif (simdjson::SUCCESS != js["${key}"].get(array) || !js["${key}"].is_array()) {
\t\t\tif (${required}) { std::cerr << "not find [${key}]" << std::endl; }
\t\t} else {
\t\t\tsize_t len = array.size();
\t\t\tfor (size_t i = 0; i < len; i++) {
\t\t\t\tbool val = false;
\t\t\t\tif (array.at(i).is_bool()) { if (simdjson::SUCCESS == array.at(i).get(val)) { tst.${key}.push_back(val); } }
\t\t\t}
\t\t}
\t}
""")

get_list_int_value_tp = Template("""\t{
\t\tsimdjson::dom::array array;
\t\tif (simdjson::SUCCESS != js["${key}"].get(array) || !js["${key}"].is_array()) {
\t\t\tif (${required}) { std::cerr << "not find [${key}]" << std::endl; }
\t\t} else {
\t\t\tsize_t len = array.size();
\t\t\tfor (size_t i = 0; i < len; i++) {
\t\t\t\t${full_type} val = 0;
\t\t\t\tif (array.at(i).is_number()) { if (simdjson::SUCCESS == array.at(i).get(val)) { tst.${key}.push_back(static_cast<${subtype}>(val)); } }
\t\t\t}
\t\t}
\t}
""")

get_list_str_value_tp = Template("""\t{
\t\tsimdjson::dom::array array;
\t\tif (simdjson::SUCCESS != js["${key}"].get(array) || !js["${key}"].is_array()) {
\t\t\tif (${required}) { std::cerr << "not find [${key}]" << std::endl; }
\t\t} else {
\t\t\tsize_t len = array.size();
\t\t\tfor (size_t i = 0; i < len; i++) {
\t\t\t\tconst char* val = nullptr;
\t\t\t\if (array.at(i).is_string()) { if (simdjson::SUCCESS == array.at(i).get(val) && val) { tst.${key}.push_back(val); } }
\t\t\t}
\t\t}
\t}
""")

get_list_object_value_tp = Template("""\t{
\t\tsimdjson::dom::array array;
\t\tif (simdjson::SUCCESS != js["${key}"].get(array) || !js["${key}"].is_array()) {
\t\t\tif (${required}) { std::cerr << "not find [${key}]" << std::endl; }
\t\t} else {
\t\t\tsize_t len = array.size();
\t\t\tfor (size_t i = 0; i < len; i++) {
\t\t\t\tsimdjson::dom::element val;
\t\t\t\tif (array.at(i).is_object()) {
\t\t\t\t\tif (simdjson::SUCCESS == array.at(i).get(val)) {
\t\t\t\t\t\t${subtype} o;
\t\t\t\t\t\tif (json2struct(val, o)) { tst.${key}.push_back(o); }
\t\t\t\t\t}
\t\t\t\t}
\t\t\t}
\t\t}
\t}
""")

get_object_value_tp = Template("""\t{
\t\tsimdjson::dom::element val;
\t\tif (simdjson::SUCCESS != js["${key}"].get(val) || !js["${key}"].is_object()) {
\t\t\tif (${required}) { std::cerr << "not find [${key}]" << std::endl; }
\t\t} else {
\t\t\t${subtype} o;
\t\t\tif (json2struct(val, o)) { tst.${key} = o; }
\t\t}
\t}
""")


def object2struct(name: str, obj: Dict[str, NodeAttr], desc: str):
    text = str()
    find = False

    # 查找该结构体是否定义
    for item in global_struct_def:
        if item.__contains__(name):
            return

    # 构造结构体
    text = f'typedef struct {name}_s {{\n'
    constructor_code = f'\t{name}_s() {{'
    if desc:
        text = f'/// {desc}\n{text}'
    for key, value in obj.items():
        if value.type in basic_inttypes:
            code = f'{value.type} {key};'
            if value.desc:
                code = f'{code:64s}///< {value.desc}\n'
            else:
                code += '\n'
            if value.type == str_t:
                constructor_code = f'{constructor_code}\n\t\t{key} = "{value.default_value}";'
            else:
                constructor_code = f'{constructor_code}\n\t\t{key} = {value.default_value};'
            text = f'{text}\t{code}'
        elif list_t == value.type:
            # 如果是数组
            code = f'std::vector<{value.subtype_name}> {key};'
            if value.desc:
                code = f'{code:64s}///< {value.desc}\n'
            else:
                code += '\n'
            text = f'{text}\t{code}'
            # 数组子类型如果是对象，不支持嵌套数组
            if not isinstance(value.subtype, str):
                object2struct(value.subtype_name, value.subtype, value.desc)
        elif object_t == value.type:
            # 如果是对象
            code = f'{value.subtype_name} {key};'
            if value.desc:
                code = f'{code:64s}///< {value.desc}\n'
            else:
                code += '\n'
            text = f'{text}\t{code}'
            object2struct(value.subtype_name, value.subtype, value.desc)

    text = f'{text}{constructor_code}\n\t}}\n}} {name};\n\n'

    # 没定义则放到全局定义中
    temp = dict()
    temp[name] = text
    global_struct_def.append(temp)


def jsonobject2struct(name: str, obj: Dict[str, NodeAttr]):
    text = str()
    find = False

    # 构造转换
    # 查找该接口是否定义
    for item in global_json2struct_code:
        if item.__contains__(name):
            return

    text = f'template <> bool json2struct<{global_ns}{name}>(simdjson::dom::element &js, {name} &st) {{\n\t{name} tst;\n'
    code = str()
    for key, value in obj.items():
        if value.type in inttypes:
            code = f'{code}{get_int_value_tp.substitute(full_type=int64_t, key=key, required=value.require, default_value=value.default_value, type=value.type)} '
        elif value.type in uinttypes:
            code = f'{code}{get_int_value_tp.substitute(full_type=uint64_t, key=key, required=value.require, default_value=value.default_value, type=value.type)} '
        elif value.type in ftypes:
            code = f'{code}{get_int_value_tp.substitute(full_type=double_t, key=key, required=value.require, default_value=value.default_value, type=value.type)} '
        elif boolean_t == value.type:
            code = f'{code}{get_bool_value_tp.substitute(key=key, required=value.require, default_value=value.default_value)} '
        elif str_t == value.type:
            code = f'{code}{get_str_value_tp.substitute(key=key, required=value.require, default_value=value.default_value, type=value.type)} '
        elif list_t == value.type:
            if value.type in inttypes:
                code = f'{code}{get_list_int_value_tp.substitute(full_type=int64_t, key=key, required=value.require, subtype=value.subtype_name)}'
            elif value.type in uinttypes:
                code = f'{code}{get_list_int_value_tp.substitute(full_type=uint64_t, key=key, required=value.require, subtype=value.subtype_name)}'
            elif boolean_t == value.type:
                code = f'{code}{get_list_bool_value_tp.substitute(key=key, required=value.require)} '
            elif value.type in ftypes:
                code = f'{code}{get_list_int_value_tp.substitute(full_type=double_t, key=key, required=value.require, subtype=value.subtype_name)} '
            elif str_t == value.subtype_name:
                code = f'{code}{get_list_str_value_tp.substitute(key=key, required=value.require)}'
            else:
                jsonobject2struct(value.subtype_name, value.subtype)
                code = f'{code}{get_list_object_value_tp.substitute(key=key, required=value.require, subtype=value.subtype_name)}'
        elif object_t == value.type:
            jsonobject2struct(value.subtype_name, value.subtype)
            code = f'{code}{get_object_value_tp.substitute(key=key, required=value.require, subtype=value.subtype_name)}'
    text = f'{text}{code}\n\tst = tst;\n\treturn true;\n}}\n\n'

    # 没定义则放到全局定义中
    temp = {
        name: {
            "code": text,
            "decl": f'template <> bool json2struct<{global_ns}{name}>(simdjson::dom::element &js, {name} &st);\n'
        }
    }
    global_json2struct_code.append(temp)


def struct2jsonobject(name: str, obj: Dict[str, NodeAttr]):
    text = str()
    find = False

    # 构造转换
    # 查找该接口是否定义
    for item in global_struct2json_code:
        if item.__contains__(name):
            return

    text = f'template <> bool struct2json<{global_ns}{name}>(const {name} &st, nlohmann::json &js) {{\n'
    code = str()

    for key, value in obj.items():
        if value.type in inttypes or value.type in uinttypes or value.type in ftypes or value.type == boolean_t or value.type == str_t:
            code = f'{code}{convert_nor_tp.substitute(key=key)}\n'
        elif value.type == object_t:
            struct2jsonobject(value.subtype_name, value.subtype)
            code = f'{code}{convert_object_tp.substitute(key=key)}\n'
        elif value.type == list_t:
            if value.subtype in inttypes or value.subtype in uinttypes or value.subtype in ftypes or value.subtype == boolean_t or value.subtype == str_t:
                code = f'{code}{convert_list_nor_tp.substitute(key=key)}\n'
            else:
                struct2jsonobject(value.subtype_name, value.subtype)
                code = f'{code}{convert_list_object_tp.substitute(key=key)}\n'

    text = f'{text}{code}\n\treturn true;\n}}\n\n'

    # 没定义则放到全局定义中
    temp = {
        name: {
            "code": text,
            "decl": f'template <> bool struct2json<{global_ns}{name}>(const {name} &st, nlohmann::json &js);\n'
        }
    }
    global_struct2json_code.append(temp)


def py2struct():
    # 定义所有结构体
    object2struct(ITEM_STRUCT_NAME, AppCfgParamSet, "应用配置参数")


def json2struct():
    # json转结构体
    jsonobject2struct(ITEM_STRUCT_NAME, AppCfgParamSet)


def struct2json():
    # 结构体转json
    struct2jsonobject(ITEM_STRUCT_NAME, AppCfgParamSet)


def write_file():
    def_file = "#pragma once\n\n#include <stdint.h>\n#include <vector>\n#include <string>\n\n"
    ns = namespace.split('.')
    ns_code = str()
    if ns:
        ns_code = 'namespace '
    # 命名空间
    for i in ns:
        ns_code = f'{ns_code}{i} {{ '
    def_file = f'{def_file}{ns_code}\n\n'
    for item in global_struct_def:
        for key, value in item.items():
            def_file = f'{def_file}{value}'
    for i in ns:
        def_file = f'{def_file}}}'
    def_file += '\n'

    # json2struct接口文件
    json2struct_h = f'#pragma once\n\n#include "{STRUCT_DEFINE_FILENAME}"\n#include "simdjson.h"\n\n{ns_code}\n{json2struct_template}\n'
    # json2struct定义文件
    json2struct_cpp = f'#include "{JSON_TO_STRUCT_FILENAME}.h"\n#include <iostream>\n\n{ns_code}\n\n'
    for item in global_json2struct_code:
        for key, value in item.items():
            json2struct_cpp = f'{json2struct_cpp}{value["code"]}'
            json2struct_h = f'{json2struct_h}{value["decl"]}'

    json2struct_h += '\n'
    for i in ns:
        json2struct_h = f'{json2struct_h}}}'
        json2struct_cpp = f'{json2struct_cpp}}}'
    json2struct_h += '\n'
    json2struct_cpp += '\n'

    # struct2json接口文件
    struct2json_h = f'#pragma once\n\n#include "{STRUCT_DEFINE_FILENAME}"\n#include "nlohmann/json.hpp"\n\n{ns_code}\n{struct2json_template}\n'
    # struct2json定义文件
    struct2json_cpp = f'#include "{STRUCT_TO_JSON_FILENAME}.h"\n\n{ns_code}\n\n'
    for item in global_struct2json_code:
        for key, value in item.items():
            struct2json_cpp = f'{struct2json_cpp}{value["code"]}'
            struct2json_h = f'{struct2json_h}{value["decl"]}'

    struct2json_h += '\n'
    for i in ns:
        struct2json_cpp = f'{struct2json_cpp}}}'
        struct2json_h = f'{struct2json_h}}}'
    struct2json_h += '\n'
    struct2json_cpp += '\n'

    # 写文件
    with open(f'{STRUCT_DEFINE_FILENAME}', 'w') as f:
        f.write(def_file)
    with open(f'{JSON_TO_STRUCT_FILENAME}.h', 'w') as f:
        f.write(json2struct_h)
    with open(f'{JSON_TO_STRUCT_FILENAME}.cpp', 'w') as f:
        f.write(json2struct_cpp)
    with open(f'{STRUCT_TO_JSON_FILENAME}.h', 'w') as f:
        f.write(struct2json_h)
    with open(f'{STRUCT_TO_JSON_FILENAME}.cpp', 'w') as f:
        f.write(struct2json_cpp)


def py2cpp():
    ns = namespace.split('.')
    global global_ns
    global_ns = '::'.join(ns)
    if global_ns:
        global_ns += "::"
    py2struct()
    json2struct()
    struct2json()
    write_file()
