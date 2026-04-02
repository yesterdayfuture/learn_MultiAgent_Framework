"""
使用单一代理，使用记忆
"""
from typing import Any, Dict, List

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily


import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

print(os.path.dirname(os.path.dirname(__file__)))

# 定义模型
model_client = OpenAIChatCompletionClient(
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


# 初始化记忆
user_memory = ListMemory()


# 定义工具
async def get_weather(city: str, units: str = "imperial") -> str:
    if units == "imperial":
        return f"The weather in {city} is 73 °F and Sunny."
    elif units == "metric":
        return f"The weather in {city} is 23 °C and Sunny."
    else:
        return f"Sorry, I don't know the weather in {city}."


assistant_agent = AssistantAgent(
    name="assistant_agent",
    model_client=model_client,
    tools=[get_weather],
    memory=[user_memory],
)


# What is the weather in New York?
async def main():
    # 新增用户消息到记忆中
    await user_memory.add(MemoryContent(content="The weather should be in metric units", mime_type=MemoryMimeType.TEXT))

    await user_memory.add(MemoryContent(content="Meal recipe must be vegan", mime_type=MemoryMimeType.TEXT))

    while True:
        message = input("请输入：")
        if message.lower() in ("bye", "quit", "exit", "q"):
            print("Bye")
            break

        # async for message in team.run_stream(task=message):  # type: ignore
        #     if isinstance(message, TaskResult):
        #         print("Stop Reason:", message.stop_reason)
        #     else:
        #         print(message)
        await Console(assistant_agent.run_stream(task=message))

        print("*"*50)
        # 查看代理的上下文，检测是否使用记忆
        context_info = await assistant_agent._model_context.get_messages()
        print(f"Memory:\n{context_info}")

        print("*" * 50)
        # 查看用户记忆
        print(f"Memory:\n{user_memory.content}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
