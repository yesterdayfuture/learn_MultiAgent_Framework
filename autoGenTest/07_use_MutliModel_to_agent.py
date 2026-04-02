"""
处理图片信息，使用多模态模型
"""
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_core.models import ModelFamily
from autogen_agentchat.messages import MultiModalMessage
from autogen_agentchat.agents import AssistantAgent

from io import BytesIO

import requests
from autogen_core import Image as AGImage
from PIL import Image
import os

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))



# 定义模型
model = OpenAIChatCompletionClient(
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


# pil_image = Image.open(BytesIO(requests.get("https://img1.baidu.com/it/u=2172818577,3783888802&fm=253&app=138&f=JPEG?w=800&h=1422").content))

with open("/Users/zhangtian/Downloads/gw/test2.png", "rb") as f:
    pil_image = Image.open(BytesIO(f.read()))

img = AGImage(pil_image)
multi_modal_message = MultiModalMessage(content=["你是一位军事信息专家和图片阅读大师，请详细描述一下这张图片,输出图片中都包含哪些物体、物体的位置、数量、当前状态等信息?", img], source="User")

# 定义智能体
agent = AssistantAgent(
    name="assistant1",
    model_client=model,
    system_message="你是一个万能助手",
    reflect_on_tool_use=True,
    model_client_stream=False
)


async def main():
    result = await agent.run(task=multi_modal_message)
    print(result.messages[-1].content)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

