"""
使用团队代理，即多智能体协作, 使用magentic-one团队，由中控智能体进行调度
"""
from typing import Any, Dict, List

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage, TextMessage
from autogen_agentchat.teams import Swarm, MagenticOneGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
# 引入BufferedChatCompletionContext, 用于缓存模型输出,让智能体使用上下文
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_core.models import ModelFamily
from autogen_agentchat.base import TaskResult

# 引入团队代理和条件
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination, MaxMessageTermination

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


# 定义工具
async def get_stock_data(symbol: str) -> Dict[str, Any]:
    """Get stock market data for a given symbol"""
    return {"price": 180.25, "volume": 1000000, "pe_ratio": 65.4, "market_cap": "700B"}


async def get_news(query: str) -> List[Dict[str, str]]:
    """Get recent news articles about a company"""
    return [
        {
            "title": "Tesla Expands Cybertruck Production",
            "date": "2024-03-20",
            "summary": "Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.",
        },
        {
            "title": "Tesla FSD Beta Shows Promise",
            "date": "2024-03-19",
            "summary": "Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.",
        },
        {
            "title": "Model Y Dominates Global EV Sales",
            "date": "2024-03-18",
            "summary": "Tesla's Model Y becomes best-selling electric vehicle worldwide, capturing significant market share.",
        },
    ]


# 定义智能体
assistant = AssistantAgent(
        "Assistant",
        model_client=model_client,
    )
team = MagenticOneGroupChat([assistant], model_client=model_client)


# Provide a different proof for Fermat's Last Theorem
async def main():

    while True:
        message = input("请输入：")
        if message.lower() in ("bye", "quit", "exit", "q"):
            print("Bye")
            break

        await team.reset()  # 重置团队代理状态

        # async for message in team.run_stream(task=message):  # type: ignore
        #     if isinstance(message, TaskResult):
        #         print("Stop Reason:", message.stop_reason)
        #     else:
        #         print(message)
        await Console(team.run_stream(task=message))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
