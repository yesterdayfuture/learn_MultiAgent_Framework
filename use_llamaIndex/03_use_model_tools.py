"""
开始学习使用 llamaIndex, 使用工具
pip install llama-index
pip install llama-index-llms-openai
"""

from llama_index.llms.openai import OpenAI
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


tool = FunctionTool.from_defaults(fn=generate_song)


# 普通聊天
result = model_client.predict_and_call(
    tools=[tool],
    messages=[
        ChatMessage(role=MessageRole.USER, content="Pick a random song for me"),
    ],
)

print(str(result))
