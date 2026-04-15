"""
初步使用 模型, 将对话历史持久化存储，并加入对话上下文中
"""
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai.like import OpenAILike
from agno.db.sqlite import SqliteDb

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


# 初始化代理
client_agent = Agent(
    session_id="test",
    name="Researcher",              # 代理名称
    role="Research information",    # 代理角色
    model=client_model,             # 模型
    # 如果模型调用失败，则使用 fallback_models
    fallback_models=[OpenAILike(
        base_url=os.getenv("base_url"),
        api_key=os.getenv("api_key"),
        id=os.getenv("model_name_2"),
    ),],
    db=SqliteDb("./custom/db.sqlite", session_table="session_table"),      # 数据库地址，建立连接; session_table表来存储会话信息
    add_history_to_context=True,            # 将对话历史加入对话上下文中
    num_history_messages=3,                 # 添加入上下文中的指定对话运行次数中的最大对话历史数量
    num_history_runs=3,                     # 添加上下文中的对话运行次数
    max_tool_calls_from_history=3,          # 从对话历史中获取工具调用数量
    read_chat_history=True,                 # 代理可以在需要上下文时调用get_chat_history()，而不是在每个请求中都包含历史记录。
)


if __name__ == "__main__":
    # # 非流式调用
    # nostreaming_result = client_agent.run("你好，我是wjm", max_tokens=1000)
    # print(f"assitant:  {nostreaming_result.content}")
    # nostreaming_result = client_agent.run("你知道我叫什么吗", max_tokens=1000)
    # print(f"assitant:  {nostreaming_result.content}")

    # 获取用户、智能助手 对话历史
    history_chat = client_agent.get_chat_history(session_id="test")
    print(f"对话历史：{history_chat}")

    # 获取当前 会话id 的所有消息
    messages = client_agent.get_session_messages(session_id="test")
    print(f"当前会话id 的所有消息：{messages}")

    # 获取最后一次输出的内容
    last_run = client_agent.get_last_run_output(session_id="test")
    print(f"最后一次输出的内容：{last_run}")

    # 检索会话
    session_id = "test12"
    session = client_agent.get_session(session_id=session_id)
    if session:
        print(f"会话ID： {session.session_id}")
        print(f"当前会话最后一次运行的消息和回复： {session.runs}")  # List of runs with messages and responses

    else:
        print(f"未找到会话 {session_id}")

