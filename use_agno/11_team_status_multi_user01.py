"""
共享状态
如何为不同用户和会话设置和管理会话状态。它展示了如何在运行期间传递会话状态，以及如何在同一会话内的多次交互中保持会话状态。
"""

from agno.models.openai import OpenAIResponses
from agno.agent import Agent
from agno.team import Team
from agno.run import RunContext
import os
from dotenv import load_dotenv
from agno.models.openai.like import OpenAILike
from agno.db.sqlite import SqliteDb
from agno.db.in_memory import InMemoryDb


load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# 支持 openai格式 的模型，使用 OpenAILike 来进行调用
# 初始化模型
client_model = OpenAILike(
    base_url=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    id=os.getenv("model_name"),
    cache_response=True,        # 缓存结果
    cache_ttl=60 * 60 * 24,     # 缓存过期时间
    cache_dir="./custom/cache"  # 缓存存放目录
)


team = Team(
    db=InMemoryDb(),
    model=client_model,
    members=[],
    instructions="我的名字是 {user_name} ，年龄是 {age}",
)

# Sets the session state for the session with the id "user_1_session_1"
team.print_response(
    "我的名字是什么",
    session_id="user_1_session_1",
    user_id="user_1",
    session_state={"user_name": "John", "age": 30},
)

# Will load the session state from the session with the id "user_1_session_1"
team.print_response("我多大了", session_id="user_1_session_1", user_id="user_1")

# Sets the session state for the session with the id "user_2_session_1"
team.print_response(
    "我的名字是什么",
    session_id="user_2_session_1",
    user_id="user_2",
    session_state={"user_name": "Jane", "age": 25},
)

# Will load the session state from the session with the id "user_2_session_1"
team.print_response("我多大了", session_id="user_2_session_1", user_id="user_2")