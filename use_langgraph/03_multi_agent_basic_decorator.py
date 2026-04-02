"""
基础的多智能体, 流式输出和非流式输出,添加装饰器来实时监测数据
"""

from typing import Annotated, List, TypedDict, Any
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
import operator
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


# ============ 1. 定义装饰器 ============
def trace_node(node_name: str = None, verbose: bool = True):
    """
    节点追踪装饰器，自动记录节点的输入、输出和执行时间
    :param node_name: 节点名称，默认使用函数名
    :param verbose: 是否打印详细信息
    """
    def decorator(func):
        # 确定节点显示名称
        display_name = node_name or func.__name__

        def wrapper(state: dict) -> dict:
            # 记录开始时间和输入
            start_time = datetime.now()
            if verbose:
                print(f"\n{'='*50}")
                print(f"🔵 节点 [{display_name}] 开始执行")
                print(f"📥 输入: {_truncate(state)}")
                print(f"{'='*50}")

            try:
                # 执行原节点函数
                result = func(state)

                # 计算耗时
                elapsed = (datetime.now() - start_time).total_seconds()

                if verbose:
                    print(f"\n{'='*50}")
                    print(f"🟢 节点 [{display_name}] 执行完成 (耗时: {elapsed:.3f}s)")
                    print(f"📤 输出: {_truncate(result)}")
                    print(f"{'='*50}")

                return result

            except Exception as e:
                if verbose:
                    print(f"\n{'='*50}")
                    print(f"❌ 节点 [{display_name}] 执行出错: {e}")
                    print(f"{'='*50}")
                raise

        return wrapper
    return decorator


def _truncate(obj: Any, max_len: int = 500) -> str:
    """安全截断长内容"""
    s = str(obj)
    return s[:max_len] + "..." if len(s) > max_len else s


# ============ 2. 定义状态 ============
class DataState(TypedDict):
    """
    数据状态
    """
    data: str
    logs: Annotated[list, operator.add]


# ============ 3. 初始化 LLM ============
client = ChatOpenAI(
    base_url=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    model=os.getenv("model_name"),
    # streaming=True,          # 如需流式输出可开启
    # stream_options={"include_usage": True},
)


# ============ 4. 定义节点（使用装饰器） ============
@trace_node("start_node")
def start_node(state: DataState) -> dict:
    """
    开始节点：根据主题生成文章
    """
    state["logs"].append(("inputs", state['data']))  # 记录原始输入
    result = client.invoke(
        input=[
            {"role": "system", "content": "你是一个文章编写大师，给你一个主题，生成一个100字左右的文章。"},
            {"role": "user", "content": f"{state['logs'][0][1]}"}
        ]
    )

    return {
        "data": result.content,
        "logs": [("start_node", result.content)]
    }


@trace_node("middle_node")
def middle_node(state: DataState) -> dict:
    """
    中间节点：对文章进行评分
    """
    result = client.invoke(
        input=[
            {"role": "system", "content": "你是一个文章评分助手，对下方用户输入的文章进行打分(1-10)，只输出一个数字"},
            {"role": "user", "content": f"{state['data']}"}
        ]
    )

    return {
        "data": result.content,
        "logs": [("middle_node", result.content)]
    }


# ============ 5. 条件边 ============
def condation_edge(state: DataState):
    score = int(state['data'])
    if score > 6:
        return END
    else:
        return "start_node"


# ============ 6. 构建图 ============
def create_graph():
    graph = StateGraph(DataState)

    # 添加节点
    graph.add_node("start_node", start_node)
    graph.add_node("middle_node", middle_node)

    # 设置入口
    graph.add_edge(START, "start_node")
    graph.add_edge("start_node", "middle_node")
    graph.add_conditional_edges("middle_node", condation_edge)

    return graph.compile()


# ============ 7. 运行 ============
if __name__ == "__main__":
    # 创建图实例
    graph = create_graph()

    # 初始状态
    inputs = DataState(
        data="描述一下机器学习",
        logs=[]
    )

    # 运行（无需传入回调）
    result = graph.invoke(input=inputs)

    print("\n" + "=" * 50)
    print("✅ 最终结果:")
    print(f"文章评分: {result['data']}")
    print(f"执行日志: {result['logs']}")