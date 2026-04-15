"""
自定义实现工具包
"""
from typing import List

from agno.agent import Agent
from agno.tools import Toolkit
from agno.utils.log import logger
from agno.models.openai.like import OpenAILike
import os
from dotenv import load_dotenv

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


class ShellTools(Toolkit):
    def __init__(self, working_directory: str = "./custom", **kwargs):
        self.working_directory = working_directory

        tools = [
            self.run_shell_command,
            self.list_files,
        ]

        super().__init__(name="shell_tools", tools=tools, **kwargs)

    def list_files(self, directory: str):
        """
        List the files in the given directory.

        Args:
            directory (str): The directory to list the files from.
        Returns:
            str: The list of files in the directory.
        """
        import os

        # List files relative to the toolkit's working_directory
        path = os.path.join(self.working_directory, directory)
        try:
            files = os.listdir(path)
            return "\n".join(files)
        except Exception as e:
            logger.warning(f"Failed to list files in {path}: {e}")
            return f"Error: {e}"
        return os.listdir(directory)

    def run_shell_command(self, args: List[str], tail: int = 100) -> str:
        """
        Runs a shell command and returns the output or error.

        Args:
            args (List[str]): The command to run as a list of strings.
            tail (int): The number of lines to return from the output.
        Returns:
            str: The output of the command.
        """
        import subprocess

        logger.info(f"Running shell command: {args}")
        try:
            logger.info(f"Running shell command: {args}")
            result = subprocess.run(args, capture_output=True, text=True, cwd=self.working_directory)
            logger.debug(f"Result: {result}")
            logger.debug(f"Return code: {result.returncode}")
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            # return only the last n lines of the output
            return "\n".join(result.stdout.split("\n")[-tail:])
        except Exception as e:
            logger.warning(f"Failed to run shell command: {e}")
            return f"Error: {e}"


agent = Agent(
    model=client_model,
    tools=[ShellTools()],
    markdown=True
)

agent.print_response("List all the files in current directory.")