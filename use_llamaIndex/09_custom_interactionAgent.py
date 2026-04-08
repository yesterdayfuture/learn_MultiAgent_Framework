import asyncio
from typing import Dict


class InteractiveAgent:
    def __init__(self):
        self.pending: Dict[str, asyncio.Future] = {}

    async def dangerous_task(self):
        print("执行危险任务...")
        # 创建 Future，等待用户输入
        fut = asyncio.get_running_loop().create_future()
        request_id = "dangerous_confirm"
        self.pending[request_id] = fut
        # 提示用户（实际应由外部显示，这里可以发事件或直接 print）
        print("Are you sure? (yes/no): ", end="", flush=True)
        # 等待外部设置结果
        user_response = await fut
        del self.pending[request_id]
        if user_response.strip().lower() == "yes":
            return "任务完成"
        else:
            return "任务取消"

    async def run(self):
        # 启动工具协程
        task = asyncio.create_task(self.dangerous_task())
        # 独立处理 stdin 输入（实际应使用 asyncio 的线程安全输入）
        while not task.done():
            # 如果有等待中的请求，读取用户输入
            if self.pending:
                # 这里简化：只处理第一个等待的请求
                rid = next(iter(self.pending))
                user_input = await asyncio.to_thread(input, "")  # 阻塞但不阻塞事件循环
                self.pending[rid].set_result(user_input)
            await asyncio.sleep(0.1)
        result = await task
        print(result)

async def main():
    agent = InteractiveAgent()
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())