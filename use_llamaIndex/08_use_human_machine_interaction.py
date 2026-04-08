"""
智能体中人机交互
"""
import os
from dotenv import load_dotenv

from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context
from llama_index.core.workflow import JsonPickleSerializer, JsonSerializer
from llama_index.core.tools import FunctionTool
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.workflow import (
    InputRequiredEvent,
    HumanResponseEvent,
)

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


# 定义工具
# a tool that performs a dangerous task
async def dangerous_task(ctx: Context) -> str:
    """A dangerous task that requires human confirmation."""

    print("dangerous_task called")

    # emit an event to the external stream to be captured
    ctx.write_event_to_stream(
        InputRequiredEvent(
            prefix="Are you sure you want to proceed? ",
            user_name="Laurie",
        )
    )

    # wait until we see a HumanResponseEvent
    response = await ctx.wait_for_event(
        HumanResponseEvent, requirements={"user_name": "Laurie"}
    )

    # act on the input from the event
    if response.response.strip().lower() == "yes":
        return "Dangerous task completed successfully."
    else:
        return "Dangerous task aborted."

llm = OpenAI(
    api_base=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    model=os.getenv("model_name_2"),
)

workflow = AgentWorkflow.from_tools_or_functions(
    [dangerous_task],
    llm=llm,
)

async def main():
    # 为工作流创建一个上下文
    ctx = Context(workflow)
    print(f"ctx的方法：{dir(ctx)}")

    handler = workflow.run(
        user_msg="I want to proceed with the dangerous task.",
        chat_history=[
            ChatMessage(role=MessageRole.USER, content="You are a helpful assistant that can perform dangerous tasks.")
        ],
        # ctx=ctx
    )

    # handle streaming output
    async for event in handler.stream_events():
        # capture InputRequiredEvent
        if isinstance(event, InputRequiredEvent):
            # capture keyboard input
            response = input(event.prefix)
            # send our response back
            handler.ctx.send_event(
                HumanResponseEvent(
                    response=response,
                    user_name=event.user_name,
                )
            )

    response = await handler
    print(str(response))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())