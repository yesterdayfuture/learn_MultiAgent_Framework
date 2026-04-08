"""
智能体中使用状态
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


# 初始化模型
llm = OpenAI(
    api_base=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    model=os.getenv("model_name_2"),
)


finance_tools = [FunctionTool.from_defaults(fn=multiply), FunctionTool.from_defaults(fn=add)]

# 创建工作流 智能体
workflow = AgentWorkflow.from_tools_or_functions(
    finance_tools,
    llm=llm,
)

# 为工作流创建一个上下文
ctx = Context(workflow)


async def main():
    response = await workflow.run(
        user_msg="Hi, my name is Laurie!",
        chat_history=[
            ChatMessage(role=MessageRole.USER, content="You are an agent that can perform basic mathematical operations using tools.")
        ],
        ctx=ctx)
    print(response)

    response2 = await workflow.run(
        user_msg="What's my name?",
        ctx=ctx)
    print(response2)

    # 将上下文信息转为字典
    ctx_dict = ctx.to_dict(serializer=JsonSerializer())

    # 从字典中加载上下文信息
    restored_ctx = Context.from_dict(
        workflow, ctx_dict, serializer=JsonSerializer()
    )

    response3 = await workflow.run(
        user_msg="What's my name?",
        ctx=restored_ctx)
    print(response3)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())