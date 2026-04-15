"""
使用工作流
对话式工作流

WorkflowAgent此功能允许您在工作流程中添加一个智能组件，该组件可以自动决定是否执行以下操作：
直接根据当前输入和以往工作流程结果作答。
当输入内容无法根据以往结果得到解答时，运行工作流。
"""
from agno.workflow import Workflow, Step, StepInput, StepOutput, OnReject, WorkflowAgent
from agno.workflow.types import HumanReview
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.knowledge.embedder.openai import OpenAIEmbedder
import os
from dotenv import load_dotenv
from agno.models.openai.like import OpenAILike
from agno.db.sqlite import SqliteDb


load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


# 支持 openai格式 的模型，使用 OpenAILike 来进行调用
# 初始化语言模型
client_model = OpenAILike(
    base_url=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    id=os.getenv("model_name"),
    cache_response=True,        # 缓存结果
    cache_ttl=60 * 60 * 24,     # 缓存过期时间
    cache_dir="./custom/cache"  # 缓存存放目录
)

story_writer = Agent(
    model=client_model,
    instructions="You are tasked with writing a 100 word story based on a given topic",
)

story_formatter = Agent(
    model=client_model,
    instructions="You are tasked with breaking down a short story in prelogues, body and epilogue",
)


def add_references(step_input: StepInput):
    """Add references to the story"""

    previous_output = step_input.previous_step_content

    if isinstance(previous_output, str):
        return previous_output + "\n\nReferences: https://www.agno.com"


# Create a WorkflowAgent that will decide when to run the workflow
workflow_agent = WorkflowAgent(model=client_model, num_history_runs=4)

# Create workflow with the WorkflowAgent
workflow = Workflow(
    name="Story Generation Workflow",
    description="A workflow that generates stories, formats them, and adds references",
    agent=workflow_agent,
    steps=[story_writer, story_formatter, add_references],
    db=SqliteDb(db_file="./custom/workflow.db"),
)

# First call - will run the workflow (new topic)
workflow.print_response(
    "Tell me a story about a dog named Rocky", stream=True
)

# Second call - will answer directly from history
workflow.print_response(
    "What was Rocky's personality?", stream=True
)

# Third call - will run the workflow (new topic)
workflow.print_response(
    "Now tell me a story about a cat named Luna", stream=True
)

# Fourth call - will answer directly from history
workflow.print_response(
    "Compare Rocky and Luna", stream=True
)