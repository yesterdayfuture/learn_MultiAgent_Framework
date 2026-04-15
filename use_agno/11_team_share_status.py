"""
共享状态
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


# 定义工具来共享整个团队的状态
def add_item(run_context: RunContext, item: str) -> str:
    """Add an item to the shopping list."""
    if not run_context.session_state:
        run_context.session_state = {}

    if item.lower() not in [
        i.lower() for i in run_context.session_state["shopping_list"]
    ]:
        run_context.session_state["shopping_list"].append(item)
        return f"Added '{item}' to the shopping list"
    else:
        return f"'{item}' is already in the shopping list"


def remove_item(run_context: RunContext, item: str) -> str:
    """Remove an item from the shopping list."""
    if not run_context.session_state:
        run_context.session_state = {}

    for i, list_item in enumerate(run_context.session_state["shopping_list"]):
        if list_item.lower() == item.lower():
            run_context.session_state["shopping_list"].pop(i)
            return f"Removed '{list_item}' from the shopping list"

    return f"'{item}' was not found in the shopping list"


# 创建一个智能体来管理购物中的购物清单
shopping_agent = Agent(
    name="Shopping List Agent",
    role="Manage the shopping list",
    model=client_model,
    tools=[add_item, remove_item],
)


# 定义团队级别工具
def list_items(run_context: RunContext) -> str:
    """List all items in the shopping list."""
    if not run_context.session_state:
        run_context.session_state = {}

    # Access shared state (not private state)
    shopping_list = run_context.session_state["shopping_list"]

    if not shopping_list:
        return "The shopping list is empty."

    items_text = "\n".join([f"- {item}" for item in shopping_list])
    return f"Current shopping list:\n{items_text}"


def add_chore(run_context: RunContext, chore: str) -> str:
    """将已完成的任务添加到团队的私人日志中"""
    if not run_context.session_state:
        run_context.session_state = {}

    # Access team's private state
    if "chores" not in run_context.session_state:
        run_context.session_state["chores"] = []

    run_context.session_state["chores"].append(chore)
    return f"Logged chore: {chore}"


# Create a team with both shared and private state
shopping_team = Team(
    name="Shopping Team",
    model=client_model,
    members=[shopping_agent],
    session_id="user1",
    session_state={"shopping_list": [], "chores": []},
    tools=[list_items, add_chore],
    instructions=[
        "You manage a shopping list.",
        "Forward add/remove requests to the Shopping List Agent.",
        "Use list_items to show the current list.",
        "Log completed tasks using add_chore.",
    ],
    # db=SqliteDb(db_file="./custom/shopping_team.db", session_table="shop_team_table")     # 使用持久化存储
    db=InMemoryDb()  # 使用内存存储
)

# Example usage
shopping_team.print_response("Add milk, eggs, and bread", stream=True, session_id="user1")
print(f"Shared state: {shopping_team.get_session_state(session_id='user1')}")

shopping_team.print_response("What's on my list?", stream=True, session_id="user1")

shopping_team.print_response("I got the eggs", stream=True, session_id="user1")
print(f"Shared state: {shopping_team.get_session_state(session_id='user1')}")