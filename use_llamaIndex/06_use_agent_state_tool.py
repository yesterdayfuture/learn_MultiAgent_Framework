"""
智能体中使用状态, 工具中也使用状态
"""
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context
from llama_index.core.workflow import JsonPickleSerializer, JsonSerializer
from llama_index.core.tools import FunctionTool
from llama_index.core.llms import ChatMessage, MessageRole


# 定义工具
def multiply(a: float, b: float) -> float:
    """Multiply two numbers and returns the product"""
    return a * b

def add(a: float, b: float) -> float:
    """Add two numbers and returns the sum"""
    return a + b

async def set_name(ctx: Context, name: str) -> str:
    state = await ctx.store.get("state")
    state["name"] = name
    await ctx.store.set("state", state)
    return f"Name set to {name}"


# 初始化模型
llm = OpenAI(
    api_base=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    model=os.getenv("model_name_2"),
)


finance_tools = [FunctionTool.from_defaults(fn=multiply), FunctionTool.from_defaults(fn=add), FunctionTool.from_defaults(fn=set_name)]

# 创建工作流 智能体
workflow = AgentWorkflow.from_tools_or_functions(
    finance_tools,
    llm=llm,
    initial_state={"name": "unset"},
)


async def main():
    # 为工作流创建一个上下文
    ctx = Context(workflow)
    print(f"ctx的方法：{dir(ctx)}")

    response = await workflow.run(
        user_msg="What's my name?",
        chat_history=[
            ChatMessage(role=MessageRole.USER, content="You are a helpful assistant that can set a name.")
        ],
        ctx=ctx)
    print(response)

    response2 = await workflow.run(
        user_msg="My name is Laurie",
        ctx=ctx)
    print(response2)

    # 从 ctx 上下文中获取内容
    state = await ctx.store.get("state")
    print("Name as stored in state: ", state["name"])

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())