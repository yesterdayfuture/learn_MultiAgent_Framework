"""
使用助手代理
model是openai格式的模型
    包含工具调用
"""
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


# 定义工具
async def getWeather(city: str) -> str:
    """Get the weather for a given city."""
    return f"The weather in {city} is 73 degrees and Sunny."

# 定义智能体
agent = AssistantAgent(
    name="assistant1",
    model_client=model,
    tools=[getWeather],
    system_message="你是一个万能助手",
    reflect_on_tool_use=True, # 让模型总结一下工具的输出
    model_client_stream=False
)


async def main() -> None:
    # # 流式调用
    # async for message in agent.run_stream(task="北京的天气是什么", cancellation_token=CancellationToken()):
    #     try:
    #         print(message.content)
    #     except Exception as e:
    #         continue

    # # 方式一、非流式输出
    # result = await agent.on_messages(messages=[TextMessage(content="北京的天气是什么", source="User")], cancellation_token=CancellationToken())
    # # 思考过程
    # print(result.inner_messages)
    # # 最终结果
    # print(result.chat_message.content)

    # 方式二、非流式输出
    result = await agent.run(task="北京的天气是什么", cancellation_token=CancellationToken(), output_task_messages= True)
    print(result.messages[-1].content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
