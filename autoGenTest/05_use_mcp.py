"""
使用mcp
pip install mcp
"""
from autogen_ext.tools.mcp import StreamableHttpServerParams, mcp_server_tools
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_core.models import ModelFamily
from autogen_agentchat.messages import TextMessage
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

print(os.path.dirname(os.path.dirname(__file__)))


# 连接远程mcp服务
mcp_client = StreamableHttpServerParams(
    url="http://127.0.0.1:8091/mcp",
)


# 获取工具
async def get_tools():
    remote_tools = await mcp_server_tools(mcp_client)
    for cur_tool in remote_tools:
        print(cur_tool.schema)

    return remote_tools

# 定义模型
model = OpenAIChatCompletionClient(
    base_url=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    model=os.getenv("model_name"),
    model_info={
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.GPT_4O,
        "structured_output": True,
        "multiple_system_messages": True,}
)


async def main() -> None:
    # 获取工具
    tools = await get_tools()

    # 定义智能体
    agent = AssistantAgent(
        name="assistant1",
        model_client=model,
        tools=tools,
        system_message="你是一个万能助手",
        reflect_on_tool_use=True,  # 让模型总结一下工具的输出
        model_client_stream=False
    )

    # 非流式调用
    result = await agent.run(task="北京天气怎么样")
    print(result.messages[-1].content)


if __name__ == "__main__":
    asyncio.run(main())