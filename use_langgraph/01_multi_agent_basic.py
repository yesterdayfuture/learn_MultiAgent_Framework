"""
基础的多智能体, 流式输出和非流式输出
"""

from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, START, END
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
import operator
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


@dataclass
class DataState(TypedDict):
    """
    数据状态
    """
    data: str
    logs: Annotated[list, operator.add]


client = ChatOpenAI(
    base_url=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    model=os.getenv("model_name"),
    # streaming=True,
    # stream_options={"include_usage": True},
)


def start_node(state: DataState) -> DataState:
    """
    开始节点
    """
    state["logs"].append(("inputs", state['data']))
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


def middle_node(state: DataState) -> DataState:
    """
    开始节点
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


def condation_edge(state: DataState):

    score = int(state['data'])

    if score > 6:
        return END
    else:
        return "start_node"


def create_graph():
    """
    创建图
    """
    graph = StateGraph(DataState)

    # 添加节点
    graph.add_node("start_node", start_node)
    graph.add_node("middle_node", middle_node)

    # 设置开始节点
    graph.set_entry_point("start_node")

    # 添加边
    graph.add_edge("start_node", "middle_node")
    graph.add_conditional_edges("middle_node", condation_edge)

    return graph.compile()


if __name__ == "__main__":
    # 获取编译后的状态图
    graph = create_graph()

    inputs = DataState(
        data="描述一下机器学习",
        logs=[]
    )

    # # 非流式输出
    # result = graph.invoke(inputs)
    # print(result)
    #
    # # 方式一：流式输出
    # for event in graph.stream(inputs, stream_mode="updates"):
    #     # event包含当前节点的增量更新
    #     for node_name, state_update in event.items():
    #         print(f"节点 {node_name} 更新: {state_update}")

    # 方式二：流式输出
    # for event in graph.stream(inputs, print_mode="values"):
    #     # event包含当前节点的增量更新
    #     for node_name, state_update in event.items():
    #         print(f"节点 {node_name} 更新: {state_update['data']}")

    for event in graph.stream(inputs, stream_mode="values"):
        # event包含当前节点的增量更新
        print(event["data"], end="\n")

    # # 方式三：流式输出
    # for event in graph.stream(inputs):
    #     # event包含当前节点的增量更新
    #     for node_name, state_update in event.items():
    #         print(f"节点 {node_name} 更新: {state_update}")

    # # 方式四：流式输出
    # for event in graph.stream(inputs, stream_mode="messages"):
    #     # event包含当前节点的增量更新
    #     print(event[0].content, end="", flush=True)


