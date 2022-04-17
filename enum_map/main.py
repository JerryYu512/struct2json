from enum_defs import *
from string import Template

enum_defs_file = "enum_defs.h"
hpp_file = "enum_map.hpp"
h_file = "enum_map.h"
cpp_file = "enum_map.cpp"
c_file = "enum_map_c.cpp"

hppheader = """
#pragma once
#include <stdint.h>
#include <string>
#include <map>
#include "enum_defs.h"

template <typename T>
const char* get_enum_str(T e) {
    return "";
}

template <typename T>
const char* get_enum_as_str(T e) {
    return "";
}

template <typename T>
T get_enum_value(const char* str) {
    return T();
}

template <typename T>
bool in_enum_range(T e) {
    return false;
}
"""

hheader = """
#pragma once
#include <stdint.h>
#include <stdbool.h>
#include "enum_defs.h"

#ifdef __cplusplus
extern "C" {
#endif
"""

hender = """
#ifdef __cplusplus
}
#endif
"""

hppfunc_decl = Template(
"""
template <> const char* get_enum_str<${name}>(${name} e);
template <> const char* get_enum_as_str<${name}>(${name} e);
template <> ${name} get_enum_value<${name}>(const char* str);
template <> bool in_enum_range<${name}>(${name} e);

"""
)

hfunc_decl = Template(
"""
const char* ${name}_get_enum_str(${name} e);
const char* ${name}_get_enum_as_str(${name} e);
${etype} ${name}_get_enum_value(const char* str);
bool ${name}_in_enum_range(${name} e);
"""
)

def template_hppdecl(name: str):
    return hppfunc_decl.substitute(name=name)


def template_hdecl(name: str, etype: str):
    return hfunc_decl.substitute(name=name, etype=etype)


def gen_reflection(item: EnumDef):
    code = str()
    # as srting接口实现
    define_as_string = f'template <> const char* get_enum_as_str<{item.name}>({item.name} e) {{\n\tswitch(e) {{\n'
    for l in item.enums:
        name = f'{l.name}:'
        code = f'{code}\t\tcase {name:32s} return "{item.name}::{l.name}";\n'

    define_as_string = f'{define_as_string}{code}\t\tdefault: return nullptr;\n\t}}\n}}\n\n'

    code = str()
    # string value接口实现
    define_string_value = f'template <> const char* get_enum_str<{item.name}>({item.name} e) {{\n\tswitch(e) {{\n'
    str_values = list()
    for l in item.enums:
        name = f'{l.name}:'
        if not l.string:
            if l.string in str_values:
                print(f'{item.name}::{l.name} confilict string : {l.string}')
                exit(-1)
            code = f'{code}\t\tcase {name:32s} return "{item.name}::{l.name}";\n'
        else:
            code = f'{code}\t\tcase {name:32s} return "{l.string}";\n'

    define_string_value = f'{define_string_value}{code}\t\tdefault: return nullptr;\n\t}}\n}}\n\n'
    # 字符串查值
    code = str()
    define_value = f'template <> {item.name} get_enum_value<{item.name}>(const char* str) {{\n\tstatic std::map<std::string, {item.name}> emap = {{\n'
    for l in item.enums:
        if not l.string:
            name = f'"{item.name}::{l.name}",'
            code = f'{code}\t\t{{{name:48s}{l.name}}},\n'
        else:
            name = f'"{l.string}",'
            code = f'{code}\t\t{{{name:48s}{l.name}}},\n'
    define_value = f'{define_value}{code}\t}};\n\n\tif (!str) {{ if (sizeof({item.name}) < sizeof({uint32_t})) {{ return static_cast<{item.name}>({uint64_max}); }} else {{ return static_cast<{item.name}>({uint64_max}); }} }}\n\n\tauto key = emap.find(str);\n\n\tif (emap.end() == key) {{ if (sizeof({item.name}) < sizeof({uint64_t})) {{ return static_cast<{item.name}>({uint32_max}); }} else {{ return static_cast<{item.name}>({uint64_max}); }} }}\n\n\treturn key->second;\n}}\n\n'
    # 接口范围内
    code = str()
    define_in_range = f'template <> bool in_enum_range<{item.name}>({item.name} e) {{\n\tswitch(e) {{\n'
    for l in item.enums:
        name = f'{l.name}:'
        code = f'{code}\t\tcase {name:32s} return true;\n'

    define_in_range = f'{define_in_range}{code}\t\tdefault: return false;\n\t}}\n}}\n\n'

    return define_as_string + define_string_value + define_value + define_in_range


def gen_cinterface(item: EnumDef):
    code = str()
    code = f'const char* {item.name}_get_enum_str({item.name} e) {{ return get_enum_str(e); }}\n'
    code = f'{code}const char* {item.name}_get_enum_as_str({item.name} e) {{ return get_enum_as_str(e); }}\n'
    code = f'{code}{item.etype} {item.name}_get_enum_value(const char* str) {{ return static_cast<{item.etype}>(get_enum_value<{item.name}>(str)); }}\n'
    code = f'{code}bool {item.name}_in_enum_range({item.name} e) {{ return in_enum_range(e); }}\n'
    code = f'{code}\n'

    return code


def gen_enum_map():
    # c++头文件内容
    hppcode = str()
    # c++文件内容
    cppcode = str()
    # c头文件内容，c接口
    hcode = str()
    # c头文件接口实现
    ccode = str()
    # 枚举定义内容
    defs = str()
    # 枚举类型名，用于冲突校验
    enum_names = list()
    # 枚举值名，用于冲突校验
    enum_keys = list()
    for item in EnumDefs:
        if item.name in enum_names:
            print(item.name, "confilict")
            exit(-1)
        enum_names.append(item.name)
        # cpp文件映射
        cppcode = f'{cppcode}{gen_reflection(item)}'
        # c文件接口
        ccode = f'{ccode}{gen_cinterface(item)}'

        # 枚举定义部分
        code = str()
        if item.desc:
            code = f'/// {item.desc}\n'
        # code = f'{code}enum class {item.name} : {item.etype} {{\n'
        code = f'{code}enum {item.name} {{\n'
        if item.enums:
            for l in item.enums:
                if l.name in enum_keys:
                    print(l.name, "confilict")
                    exit(-1)
                enum_keys.append(l.name)
                value = str()
                desc = str()
                # 值
                if l.value:
                    value = f'{l.name:36s}= {l.value}'
                else:
                    value = f'{l.name}'
                # 注释
                if l.desc:
                    value = f'{value},'
                    desc = f'{value:62s}///< {l.desc}'
                else:
                    desc = value
                # 单条
                code = f'{code}\t{desc}\n'
        # 最终枚举类型定义
        defs = f'{defs}{code}}};\n\n'
        # 头文件内容
        hppcode = f'{hppcode}{template_hppdecl(item.name)}'
        hcode = f'{hcode}{template_hdecl(item.name, item.etype)}'
    
    # 补充头文件完整性
    defs = f'#pragma once\n\n#include <stdint.h>\n\n{defs}'
    hppcode = f'{hppheader}\n{hppcode}'
    cppcode = f'#include "{hpp_file}"\n\n{cppcode}'
    hcode = f'{hheader}{hcode}{hender}'
    ccode = f'#include "{hpp_file}"\n#include "{h_file}"\n\n{ccode}'

    with open(enum_defs_file, 'w') as f:
        f.write(defs)

    with open(hpp_file, 'w') as f:
        f.write(hppcode)
    with open(cpp_file, 'w') as f:
        f.write(cppcode)

    with open(h_file, 'w') as f:
        f.write(hcode)
    with open(c_file, 'w') as f:
        f.write(ccode)

gen_enum_map()
