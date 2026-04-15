"""
初步使用 模型 调用工具
"""
import os
import random
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai.like import OpenAILike
from agno.tools import tool

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# 支持 openai格式 的模型，使用 OpenAILike 来进行调用
# 初始化模型
client_model = OpenAILike(
    base_url=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    id=os.getenv("model_name_2"),
    cache_response=True,        # 缓存结果
    cache_ttl=60 * 60 * 24,     # 缓存过期时间
    cache_dir="./custom/cache"  # 缓存存放目录
)


# 定义工具
def get_weather(city: str) -> str:
    """Get the weather for the given city.

    Args:
        city (str): The city to get the weather for.
    """

    # In a real implementation, this would call a weather API
    weather_conditions = ["sunny", "cloudy", "rainy", "snowy", "windy"]
    random_weather = random.choice(weather_conditions)

    return f"The weather in {city} is {random_weather}."


# 初始化代理
client_agent = Agent(
    name="Researcher",              # 代理名称
    role="Research information",    # 代理角色
    model=client_model,             # 模型
    # 如果模型调用失败，则使用 fallback_models
    fallback_models=[OpenAILike(
        base_url=os.getenv("base_url"),
        api_key=os.getenv("api_key"),
        id=os.getenv("model_name_2"),
    ),],
    tools=[get_weather],           # 工具
    markdown=True,                  # 是否使用 markdown 格式输出
)


if __name__ == "__main__":
    # client_agent.print_response("介绍一下上海天气", stream=True)

    # 流式调用
    # stream_events: 是否输出所有类型消息
    for streaming_result in client_agent.run("介绍一下上海天气", stream=True, stream_events=True):
        print(streaming_result)
        # print(streaming_result.content, end="", flush=True)



    # 非流式调用
    # response = client_agent.run("介绍一下上海天气", stream=False)
    # # 查看工具调用
    # for msg in response.messages:
    #     if msg.role == 'assistant' and msg.tool_calls:
    #         print("模型调用了工具：", msg.tool_calls)
    #     if msg.role == 'tool':
    #         print("工具返回：", msg.content)
    #
    # # 最终回答
    # print("最终回答：", response.content)
