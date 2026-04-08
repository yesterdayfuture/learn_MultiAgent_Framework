"""
开始学习使用 llamaIndex, 使用工具智能体
pip install llama-index
pip install llama-index-llms-openai
"""
import asyncio
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.llms import ChatMessage, ImageBlock, TextBlock, MessageRole
from llama_index.core.tools import FunctionTool
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

model_client = OpenAI(
    api_base=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    model=os.getenv("model_name_2"),
)


# 定义工具
def generate_song(name: str, artist: str):
    """Generates a song with provided name and artist."""
    return {"name": name, "artist": artist}


def multiply(a: float, b: float) -> float:
    """Multiply two numbers and returns the product"""
    return a * b


def add(a: float, b: float) -> float:
    """Add two numbers and returns the sum"""
    return a + b


tools = [FunctionTool.from_defaults(fn=generate_song), FunctionTool.from_defaults(fn=multiply), FunctionTool.from_defaults(fn=add)]


# 初始化 Agent
workflow = FunctionAgent(
    tools=tools,
    llm=model_client,
    system_prompt="You are an agent that can perform basic mathematical operations using tools."
)


async def main():
    result = await workflow.run(
        user_msg=ChatMessage(role=MessageRole.USER, content="What is 20+(2*4)?"),
        # chat_history=[ChatMessage(role=MessageRole.ASSISTANT, content="You are an agent that can perform basic mathematical operations using tools.")]
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
