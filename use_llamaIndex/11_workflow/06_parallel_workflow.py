"""
工作流可以并发运行步骤
"""
from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    step,
    Event,
    Context,
    Workflow
)
import asyncio
import random


class StepTwoEvent(Event):
    query: str


class StepThreeEvent(Event):
    result: str


class ConcurrentFlow(Workflow):
    @step
    async def start(self, ctx: Context, ev: StartEvent) -> StepTwoEvent:
        ctx.send_event(StepTwoEvent(query="Query 1"))
        ctx.send_event(StepTwoEvent(query="Query 2"))
        ctx.send_event(StepTwoEvent(query="Query 3"))

    @step(num_workers=4)
    async def step_two(self, ctx: Context, ev: StepTwoEvent) -> StepThreeEvent:
        print("Running query ", ev.query)
        await asyncio.sleep(random.randint(1, 5))
        return StepThreeEvent(result=ev.query)

    @step
    async def step_three(self, ctx: Context, ev: StepThreeEvent) -> StopEvent:
        # wait until we receive 3 events
        result = ctx.collect_events(ev, [StepThreeEvent] * 3)
        if result is None:
            return None

        # do something with all 3 results together
        print(result)
        return StopEvent(result="Done")


async def main():
    w = ConcurrentFlow()
    handler = w.run(first_input="Start the workflow.")
    async for ev in handler.stream_events():
        print(ev)

    final_result = await handler
    print("Final result", final_result)


if __name__ == "__main__":
    asyncio.run(main())