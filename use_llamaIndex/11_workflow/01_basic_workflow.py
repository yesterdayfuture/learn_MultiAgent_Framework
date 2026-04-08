"""
定义基础工作流

pip install llama-index-utils-workflow
"""
from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Event,
)
import asyncio
from llama_index.utils.workflow import draw_all_possible_flows


# 定义事件
class FirstEvent(Event):
    first_output: str


class SecondEvent(Event):
    second_output: str


# 定义工作流
class MyWorkflow(Workflow):
    @step
    async def step_one(self, ev: StartEvent) -> FirstEvent:
        print(ev)
        print(ev.input_content)
        return FirstEvent(first_output="First step complete.")

    @step
    async def step_three(self, ev: FirstEvent) -> SecondEvent:
        print(ev.first_output)
        return SecondEvent(second_output="Workflow complete.")

    @step
    async def step_two(self, ev: SecondEvent) -> StopEvent:
        print(ev.second_output)
        return StopEvent(result="Second step complete.")


async def main():
    w = MyWorkflow(timeout=10, verbose=False)
    result = await w.run(input_content="Start the workflow.")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

    # 绘制工作流图
    draw_all_possible_flows(MyWorkflow, filename="multi_step_workflow.html")