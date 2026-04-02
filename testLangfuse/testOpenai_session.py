"""
测试使用 langfuse 跟踪监测 openai 调用,添加session
"""
from langfuse import get_client, propagate_attributes
from langfuse.openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


# os.environ["LANGFUSE_SECRET_KEY"] = "xxx"
# os.environ["LANGFUSE_PUBLIC_KEY"] = "xxx"
# os.environ["LANGFUSE_BASE_URL"] = "xxx"



langfuse_client = get_client()


client = OpenAI(
    base_url=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city for which to get the weather."
                    }
                },
                "required": ["city"]
            }
        }
    }
]


def non_stream(user_message: str = "你叫什么名字?"):
    result = client.chat.completions.create(
        model=os.getenv("model_name"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{user_message}"}
        ]
    )
    return result.choices[-1].message.content


def chat_stream(user_message):
    messages = [{"role": "user", "content": user_message}]

    stream = client.chat.completions.create(
        model=os.getenv("model_name"),
        messages=messages,
        stream=True
    )

    # 收集流式响应
    full_response = ""

    for chunk in stream:
        delta = chunk.choices[0].delta

        # 处理内容
        if delta.content:
            full_response += delta.content
            print(delta.content, end="", flush=True)


with langfuse_client.start_as_current_observation(as_type="span", name=os.getenv("model_name")):
    with propagate_attributes(session_id="session-id"):
        # 测试
        chat_stream("你是谁？")

        # print(non_stream())