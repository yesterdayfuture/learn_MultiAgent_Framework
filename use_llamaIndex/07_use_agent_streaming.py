"""
智能体中使用状态, 工具中也使用状态,并且进行流式输出
"""
import os
from dotenv import load_dotenv

from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context
from llama_index.core.workflow import JsonPickleSerializer, JsonSerializer
from llama_index.core.tools import FunctionTool
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.agent.workflow import (
    AgentInput,
    AgentOutput,
    ToolCall,
    ToolCallResult,
    AgentStream,
)

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

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

    # 流式输出
    handler = workflow.run(
        user_msg="My name is Laurie",
        ctx=ctx)

    # handle streaming output
    async for event in handler.stream_events():
        if isinstance(event, AgentStream):
            print(event.delta, end="", flush=True)
        elif isinstance(event, AgentInput):
            print("Agent input: ", event.input)  # the current input messages
            print("Agent name:", event.current_agent_name)  # the current agent name
        elif isinstance(event, AgentOutput):
            print("Agent output: ", event.response)  # the current full response
            print("Tool calls made: ", event.tool_calls)  # the selected tool calls, if any
            print("Raw LLM response: ", event.raw)  # the raw llm api response
        elif isinstance(event, ToolCallResult):
            print("Tool called: ", event.tool_name)  # the tool name
            print("Arguments to the tool: ", event.tool_kwargs)  # the tool kwargs
            print("Tool output: ", event.tool_output)  # the tool output

    # print final output
    print(str(await handler))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())