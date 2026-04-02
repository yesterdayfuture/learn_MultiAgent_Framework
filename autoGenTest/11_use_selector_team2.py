"""
使用团队代理，即多智能体协作, 使用选择器团队，由中控智能体进行调度,使用自定义选择函数，添加用户反馈
自定义选择函数作用：
    如果最后一条消息是 planning_agent 生产的时候，如果它的前一条信息是用户输入，则听中控智能体的调度；否则，执行 user_proxy_agent
    如果最后一条消息是用户输入时，如果包含 APPROVE 时，听中控智能体的调度；如果不包含 APPROVE，则由 planning_agent 重新生产
"""
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
# 引入BufferedChatCompletionContext, 用于缓存模型输出,让智能体使用上下文
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_core.models import ModelFamily
from autogen_agentchat.messages import TextMessage, ChatMessage, AgentEvent
from autogen_agentchat.base import TaskResult
from typing import Sequence

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
async def getWeather(city: str) -> str:
    """Get the weather for a given city."""
    return f"The weather in {city} is 73 degrees and Sunny."


# 模拟工具
def search_web_tool(query: str) -> str:
    if "2006-2007" in query:
        return """Here are the total points scored by Miami Heat players in the 2006-2007 season:
        Udonis Haslem: 844 points
        Dwayne Wade: 1397 points
        James Posey: 550 points
        ...
        """
    elif "2007-2008" in query:
        return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214."
    elif "2008-2009" in query:
        return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398."
    return "No data found."


def percentage_change_tool(start: float, end: float) -> float:
    return ((end - start) / start) * 100


# 定义智能体
planning_agent = AssistantAgent(
    "PlanningAgent",
    description="An agent for planning tasks, this agent should be the first to engage when given a new task.",
    model_client=model_client,
    system_message="""
    You are a planning agent.
    Your job is to break down complex tasks into smaller, manageable subtasks.
    Your team members are:
        WebSearchAgent: Searches for information
        DataAnalystAgent: Performs calculations

    You only plan and delegate tasks - you do not execute them yourself.

    When assigning tasks, use this format:
    1. <agent> : <task>

    After all tasks are complete, summarize the findings and end with "TERMINATE".
    """,
)

web_search_agent = AssistantAgent(
    "WebSearchAgent",
    description="An agent for searching information on the web.",
    tools=[search_web_tool],
    model_client=model_client,
    system_message="""
    You are a web search agent.
    Your only tool is search_tool - use it to find information.
    You make only one search call at a time.
    Once you have the results, you never do calculations based on them.
    """,
)

data_analyst_agent = AssistantAgent(
    "DataAnalystAgent",
    description="An agent for performing calculations.",
    model_client=model_client,
    tools=[percentage_change_tool],
    system_message="""
    You are a data analyst.
    Given the tasks you have been assigned, you should analyze the data and provide results using the tools provided.
    If you have not seen the data, ask for it.
    """,
)


# 定义中止条件
text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=25)
termination = text_mention_termination | max_messages_termination


# 选择器提示词
selector_prompt = """Select an agent to perform task.

{roles}

Current conversation context:
{history}

Read the above conversation, then select an agent from {participants} to perform the next task.
Make sure the planner agent has assigned tasks before other agents start working.
Only select one agent.
"""

# 定义团队代理
user_proxy_agent = UserProxyAgent("UserProxyAgent", description="A proxy for the user to approve or disapprove tasks.")


# 自定义选择器函数返回None将使用默认的基于模型的选择
def selector_func_with_user_proxy(messages: Sequence[AgentEvent | ChatMessage]) -> str | None:
    if messages[-1].source != planning_agent.name and messages[-1].source != user_proxy_agent.name:
        # Planning agent should be the first to engage when given a new task, or check progress.
        return planning_agent.name
    if messages[-1].source == planning_agent.name:
        if messages[-2].source == user_proxy_agent.name and "APPROVE" in messages[-1].content.upper():  # type: ignore
            # User has approved the plan, proceed to the next agent.
            return None
        # Use the user proxy agent to get the user's approval to proceed.
        return user_proxy_agent.name
    if messages[-1].source == user_proxy_agent.name:
        # If the user does not approve, return to the planning agent.
        if "APPROVE" not in messages[-1].content.upper():  # type: ignore
            return planning_agent.name
    return None


team = SelectorGroupChat(
    [planning_agent, web_search_agent, data_analyst_agent, user_proxy_agent],
    model_client=model_client,
    termination_condition=termination,
    selector_prompt=selector_prompt,
    selector_func=selector_func_with_user_proxy,
    allow_repeated_speaker=True,
)


# Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
async def main() -> None:

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
