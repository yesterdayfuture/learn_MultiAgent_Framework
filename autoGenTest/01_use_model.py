"""
autogen 如何使用模型
pip install -U "autogen-agentchat"
pip install "autogen-ext[openai]"
"""

from autogen_core.models import UserMessage
from autogen_core.models import ModelFamily
from autogen_ext.models.openai import OpenAIChatCompletionClient

import os
import asyncio
from dotenv import load_dotenv

# 加载.env中的环境变量
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

client = OpenAIChatCompletionClient(
    base_url=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    model=os.getenv("model_name"),
    model_info={
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.O4,
        "structured_output": True,
        "multiple_system_messages": True,}
)


async def main():
    while True:
        message = input("请输入：")
        if message.lower() in ("bye", "quit", "exit", "q"):
            print("Bye")
            break
        user_message = UserMessage(content=f"{message}", source="User")
        result = await client.create(
            messages=[user_message],
        )

        print(result.content)


if __name__ == "__main__":
    asyncio.run(main())