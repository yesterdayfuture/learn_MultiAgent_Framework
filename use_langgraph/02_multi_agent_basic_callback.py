"""
基础的多智能体, 流式输出和非流式输出,添加回调函数
"""

from typing import Annotated, List, TypedDict, Any, Dict
from langgraph.graph import StateGraph, START, END
from langchain_core.callbacks import BaseCallbackHandler
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
import operator
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


# ============ 1. 定义自定义回调处理器 ============
class NodeTraceCallback(BaseCallbackHandler):
    """
    捕获每个节点执行时的输入和输出
    利用 run_id 关联开始和结束事件
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self._node_times = {}  # run_id -> start_time
        self._node_names = {}  # run_id -> node_name

    def on_chain_start(
            self,
            serialized: Dict[str, Any],
            inputs: Dict[str, Any],
            *,
            run_id: Any,
            parent_run_id: Any = None,
            tags: List[str] = None,
            metadata: Dict[str, Any] = None,
            **kwargs: Any
    ) -> None:
        """节点开始执行时调用"""
        # 获取节点名称（可能在 metadata 或 tags 中）
        node_name = None
        if metadata:
            node_name = metadata.get("langgraph_node")
        if not node_name and tags:
            # 有时节点名称会出现在 tags 中，例如 "node:research"
            for tag in tags:
                if tag.startswith("node:"):
                    node_name = tag[5:]
                    break

        if node_name:
            self._node_names[run_id] = node_name
            self._node_times[run_id] = datetime.now()
            if self.verbose:
                print(f"\n{'=' * 50}")
                print(f"🔵 节点 [{node_name}] 开始执行")
                print(f"📥 输入: {self._truncate(inputs)}")
                print(f"{'=' * 50}")

    def on_chain_end(
            self,
            outputs: Dict[str, Any],
            *,
            run_id: Any,
            parent_run_id: Any = None,
            tags: List[str] = None,
            **kwargs: Any,
    ) -> None:
        """节点执行结束时调用"""
        node_name = self._node_names.get(run_id)
        if node_name and self.verbose:
            start_time = self._node_times.get(run_id)
            elapsed = (datetime.now() - start_time).total_seconds() if start_time else 0.0

            print(f"\n{'=' * 50}")
            print(f"🟢 节点 [{node_name}] 执行完成 (耗时: {elapsed:.3f}s)")
            print(f"📤 输出: {self._truncate(outputs)}")
            print(f"{'=' * 50}")

            # 清理已使用的记录
            self._node_names.pop(run_id, None)
            self._node_times.pop(run_id, None)

    def on_chain_error(
            self,
            error: BaseException,
            *,
            run_id: Any,
            parent_run_id: Any = None,
            tags: List[str] = None,
            **kwargs: Any,
    ) -> None:
        """节点执行出错时调用"""
        node_name = self._node_names.get(run_id)
        if node_name and self.verbose:
            print(f"\n{'=' * 50}")
            print(f"❌ 节点 [{node_name}] 执行出错: {error}")
            print(f"{'=' * 50}")
            self._node_names.pop(run_id, None)
            self._node_times.pop(run_id, None)

    def _truncate(self, obj: Any, max_len: int = 500) -> str:
        """安全截断长内容"""
        s = str(obj)
        return s[:max_len] + "..." if len(s) > max_len else s

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
    # 创建回调处理器
    callback = NodeTraceCallback(verbose=True)

    # 获取编译后的状态图
    graph = create_graph()

    inputs = DataState(
        data="描述一下机器学习",
        logs=[]
    )

    # 运行并传入回调
    config = {"callbacks": [callback]}

    # 非流式输出
    result = graph.invoke(
        input=inputs,
        config=config
        )
    print(result)


