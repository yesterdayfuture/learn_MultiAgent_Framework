"""
开始学习使用 llamaIndex, 调用模型进行聊天，多模态聊天
pip install llama-index
pip install llama-index-llms-openai
"""

from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage, ImageBlock, TextBlock, MessageRole
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

model_client = OpenAI(
    api_base=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    model=os.getenv("model_name_2"),
)


# 普通聊天
result = model_client.chat(
    messages=[
        ChatMessage(role=MessageRole.USER, content="你叫什么名字?"),
    ],
)
print( result)

# 多模态聊天
multi_modal_message = [
    ChatMessage(
        role=MessageRole.USER,
        blocks=[
            TextBlock(
                text="请用中文回答，对图片内容进行描述",
            ),
            ImageBlock(
                path="img.png"
            )
        ]
    )
]

multi_result = model_client.chat(
    messages=multi_modal_message,
)
print(multi_result)
