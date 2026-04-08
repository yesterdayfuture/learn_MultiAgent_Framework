"""
创建代码执行器

为了执行代码，我们需要创建一个代码执行器。

这里，我们将使用一个简单的进程内代码执行器，它维护自己的状态。
"""
from typing import Any, Dict, Tuple
import io
import contextlib
import ast
import traceback
import sys


class SimpleCodeExecutor:
    """
    A simple code executor that runs Python code with state persistence.

    This executor maintains a global and local state between executions,
    allowing for variables to persist across multiple code runs.

    NOTE: not safe for production use! Use with caution.
    """

    def __init__(self, locals: Dict[str, Any], globals: Dict[str, Any]):
        """
        Initialize the code executor.

        Args:
            locals: Local variables to use in the execution context
            globals: Global variables to use in the execution context
        """
        # State that persists between executions
        self.globals = globals
        self.locals = locals

    def execute(self, code: str) -> Tuple[bool, str, Any]:
        """
        Execute Python code and capture output and return values.

        Args:
            code: Python code to execute

        Returns:
            Tuple (success, output, return_value)
            - success: bool indicating whether execution succeeded
            - output: captured stdout/stderr as string
            - return_value: value of the last expression (if any)
        """
        # Capture stdout and stderr
        stdout = io.StringIO()
        stderr = io.StringIO()

        success = True
        output = ""
        return_value = None

        try:
            # Execute with captured output
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                # 尝试使用 AST 变换来捕获最后一个表达式的值
                try:
                    # 解析代码为 AST
                    tree = ast.parse(code)
                    # 如果代码非空且最后一个节点是表达式，则进行变换
                    if tree.body and isinstance(tree.body[-1], ast.Expr):
                        # 创建赋值语句: __result__ = <last expression>
                        last_expr = tree.body[-1]
                        assign = ast.Assign(
                            targets=[ast.Name(id="__result__", ctx=ast.Store())],
                            value=last_expr.value,
                            lineno=last_expr.lineno,
                            col_offset=last_expr.col_offset,
                        )
                        # 替换最后一个节点
                        tree.body[-1] = assign
                        # 修复位置信息
                        ast.fix_missing_locations(tree)
                        # 编译 AST 为可执行代码对象
                        compiled = compile(tree, '<ast>', 'exec')
                        # 执行变换后的代码
                        exec(compiled, self.globals, self.locals)
                        # 获取返回值
                        return_value = self.locals.get("__result__")
                    else:
                        # 没有需要捕获的表达式，直接执行原代码
                        exec(code, self.globals, self.locals)
                except Exception as transform_err:
                    # AST 变换失败时回退到直接执行原代码（不捕获返回值）
                    # 可以打印调试信息，但生产环境可忽略
                    # print(f"AST transform failed: {transform_err}", file=sys.stderr)
                    exec(code, self.globals, self.locals)

            # 获取捕获的输出
            output = stdout.getvalue()
            if stderr.getvalue():
                if output:
                    output += "\n"
                output += stderr.getvalue()

        except Exception as e:
            # 捕获执行过程中的异常
            success = False
            output = f"Error: {type(e).__name__}: {str(e)}\n"
            output += traceback.format_exc()

        # 如果有返回值，将其追加到输出末尾（便于查看）
        if return_value is not None:
            if output:
                output += "\n\n"
            output += str(return_value)

        return success, output, return_value


# Define a few helper functions
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b


def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    return a / b


code_executor = SimpleCodeExecutor(
    # give access to our functions defined above
    locals={
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide,
    },
    globals={
        # give access to all builtins
        "__builtins__": __builtins__,
        # give access to numpy
        "np": __import__("numpy"),
    },
)


code_str = """
def fibonacci(n: int) -> int:
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

# Calculate the sum of the first 10 Fibonacci numbers
fibonacci_sum = 0
for i in range(10):
    fibonacci_sum = add(fibonacci_sum, fibonacci(i))

fibonacci_sum
"""

# 执行代码
success, output, return_value = code_executor.execute(code_str)

# 打印结果
print(f"Success: {success}")
print(f"Output:\n{output}")
print(f"Return value: {return_value}")