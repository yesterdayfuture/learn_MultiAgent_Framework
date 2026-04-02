"""
使用助手代理
model是openai格式的模型
    包含工具调用
"""
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
# 引入BufferedChatCompletionContext, 用于缓存模型输出,让智能体使用上下文
from autogen_core.model_context import BufferedChatCompletionContext
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
    model_client_stream=False,
    model_context=BufferedChatCompletionContext(buffer_size=4)
)


async def main() -> None:

    while True:
        message = input("请输入：")
        if message.lower() in ("bye", "quit", "exit", "q"):
            print("Bye")
            break
        result = await agent.run(task=message, cancellation_token=CancellationToken(), output_task_messages= True)
        print(result.messages[-1].content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
