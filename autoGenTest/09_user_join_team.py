"""
使用团队代理，即多智能体协作, 引入人工参与
"""
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
# 引入BufferedChatCompletionContext, 用于缓存模型输出,让智能体使用上下文
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_core.models import ModelFamily
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult

# 引入团队代理和条件
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination

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

agent2 = AssistantAgent(
    name="critic",
    model_client=model,
    tools=[getWeather],
    system_message="Provide constructive feedback. Respond with 'APPROVE' to when your feedbacks are addressed.",
    reflect_on_tool_use=True, # 让模型总结一下工具的输出
    model_client_stream=False,
    model_context=BufferedChatCompletionContext(buffer_size=4)
)
user_agent = UserProxyAgent(
    name="user_join",
    input_func=input
)

# 定义中止条件
text_termination = TextMentionTermination("APPROVE")

team_agent = RoundRobinGroupChat(
    participants=[agent, agent2, user_agent],
    termination_condition=text_termination,
)


async def main() -> None:

    while True:
        message = input("请输入：")
        if message.lower() in ("bye", "quit", "exit", "q"):
            print("Bye")
            break
        # result = await team_agent.run(task=message, cancellation_token=CancellationToken(), output_task_messages= True)
        # print(result.messages[-1].content)

        await team_agent.reset()  # 重置团队代理状态

        async for message in team_agent.run_stream(task=message):  # type: ignore
            if isinstance(message, TaskResult):
                print("Stop Reason:", message.stop_reason)
            else:
                print(message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
