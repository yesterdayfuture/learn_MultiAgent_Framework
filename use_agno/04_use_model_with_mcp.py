"""
初步使用 模型
"""
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai.like import OpenAILike
from agno.tools.mcp import MCPTools
import asyncio

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# 支持 openai格式 的模型，使用 OpenAILike 来进行调用
# 初始化模型
client_model = OpenAILike(
    base_url=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    id=os.getenv("model_name_2"),
    cache_response=True,        # 缓存结果
    cache_ttl=60 * 60 * 24,     # 缓存过期时间
    cache_dir="./custom/cache"  # 缓存存放目录
)


async def main():

    # 初始化工具
    mcp_tools = MCPTools(transport="streamable-http", url="http://127.0.0.1:8091/mcp")
    await mcp_tools.connect()

    # 初始化代理
    client_agent = Agent(
        name="Researcher",  # 代理名称
        role="Research information",  # 代理角色
        model=client_model,  # 模型
        # 如果模型调用失败，则使用 fallback_models
        fallback_models=[OpenAILike(
            base_url=os.getenv("base_url"),
            api_key=os.getenv("api_key"),
            id=os.getenv("model_name_2"),
        ), ],
        tools=[mcp_tools],
    )

    # 非流式调用
    response = await client_agent.arun("介绍一下今日上海天气，不要自己幻想", stream=False)
    # 查看工具调用
    for msg in response.messages:
        if msg.role == 'assistant' and msg.tool_calls:
            print("模型调用了工具：", msg.tool_calls)
        if msg.role == 'tool':
            print("工具返回：", msg.content)

    # 最终回答
    print("最终回答：", response.content)

    await mcp_tools.close()


if __name__ == "__main__":
    asyncio.run(main())
