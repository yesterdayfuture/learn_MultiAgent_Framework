"""
开始学习使用 llamaIndex, 调用模型
pip install llama-index
pip install llama-index-llms-openai
"""

from llama_index.llms.openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

model_client = OpenAI(
    api_base=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    model=os.getenv("model_name_2"),
)


# # 非流式调用
# result = model_client.complete(
#     "你叫什么名字?",
# )
# print(result)

# 流式调用
for message in model_client.stream_complete("你叫什么名字?"):
    print(message.delta, end="", flush=True)