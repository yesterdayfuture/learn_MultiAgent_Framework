"""
自动将 python 函数 转为 tool 工具
    本质上通过inspect模块实现函数信息提取
"""

from autogen_core.tools import FunctionTool
import inspect
import json
from typing import Any, Dict


# Define a tool using a Python function.
async def web_search_func(query: str) -> str:
    """Find information on the web"""
    return "AutoGen is a programming framework for building multi-agent applications."


# 自动将 python 函数 转为 tool 工具
web_search_function_tool = FunctionTool(web_search_func, description=inspect.getdoc(web_search_func))
# 查看工具信息
print(web_search_function_tool.schema)


# 使用inspect实现函数信息提取
def extract_function_info(func) -> Dict[str, Any]:
    """使用 inspect 模块提取函数信息，返回符合 OpenAI 函数调用格式的字典。"""
    # 获取函数名
    name = func.__name__

    # 获取文档字符串（描述）
    description = inspect.getdoc(func) or ""

    # 获取函数签名
    sig = inspect.signature(func)

    # 构建 parameters 字典
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }

    for param_name, param in sig.parameters.items():
        # 跳过 self 或 cls（如果有）
        if param_name in ("self", "cls"):
            continue

        # 获取参数类型
        annotation = param.annotation
        if annotation is inspect.Parameter.empty:
            param_type = "string"  # 默认类型
        else:
            # 将 Python 类型映射到 JSON 类型
            if annotation is str:
                param_type = "string"
            elif annotation is int:
                param_type = "integer"
            elif annotation is float:
                param_type = "number"
            elif annotation is bool:
                param_type = "boolean"
            elif annotation is list:
                param_type = "array"
            elif annotation is dict:
                param_type = "object"
            else:
                # 对于更复杂的类型，可以进一步处理，这里简单设为 string
                param_type = "string"

        # 构建属性的描述（如果没有文档，就用参数名作为描述）
        # 这里简单使用参数名作为 description，并设置 title 为首字母大写
        prop = {
            "type": param_type,
            "description": param_name,
            "title": param_name.capitalize(),
        }

        # 检查是否有默认值，如果没有则加入 required 列表
        if param.default is inspect.Parameter.empty:
            parameters["required"].append(param_name)

        parameters["properties"][param_name] = prop

    # 如果 required 列表为空，可以删除该字段（或保留空列表）
    if not parameters["required"]:
        parameters.pop("required", None)

    return {
        "name": name,
        "description": description,
        "parameters": parameters,
        "strict": False,
    }


# 测试
# 提取信息
info = extract_function_info(web_search_func)

# 打印结果（美化输出）
print(json.dumps(info, indent=2, ensure_ascii=False))

