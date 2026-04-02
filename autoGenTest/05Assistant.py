"""
单一智能体
"""
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_core.models import ModelFamily
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
    reflect_on_tool_use=True,
    model_client_stream=False
)


async def main() -> None:
    # await Console(agent.run_stream(task="北京的天气是什么"))

    async for message in agent.run_stream(task="北京的天气是什么"):
        try:
            print(message.content)
        except Exception as e:
            continue

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
