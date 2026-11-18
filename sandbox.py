import ast
import tempfile
import subprocess
import sys
import os

DISALLOWED_MODULES = {
    'os', 'sys', 'subprocess', 'shutil', 'socket', 'sqlite3', 
    'pathlib', 'ctypes', 'pty', 'importlib', 'inspect', 'platform', 
    'urllib', 'requests', 'http', 'asyncio', 'multiprocessing', 'threading'
}

DISALLOWED_NAMES = {
    'eval', 'exec', 'open', '__import__', 'compile', 'globals', 
    'locals', 'getattr', 'setattr', 'delattr', 'breakpoint', 'input'
}

DISALLOWED_ATTRS = {
    '__subclasses__', '__bases__', '__mro__', '__globals__', 
    '__code__', '__builtins__', '__dict__', '__class__'
}

def validate_code_safety(code_str: str) -> tuple[bool, str]:
    """
    Performs static AST analysis on candidate code before execution.
    Blocks dangerous modules, introspection tricks, and system calls.
    """
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"

    for node in ast.walk(tree):
        # 1. Block prohibited module imports (import os, import sys)
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_module = alias.name.split('.')[0].lower()
                if root_module in DISALLOWED_MODULES:
                    return False, f"Security Violation: Importing module '{alias.name}' is restricted."

        # 2. Block from x import y
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_module = node.module.split('.')[0].lower()
                if root_module in DISALLOWED_MODULES:
                    return False, f"Security Violation: Importing from module '{node.module}' is restricted."

        # 3. Block dangerous built-in names (eval, exec, open, etc.)
        elif isinstance(node, ast.Name):
            if node.id.lower() in DISALLOWED_NAMES:
                return False, f"Security Violation: Use of '{node.id}' is restricted."

        # 4. Block sandbox escape attributes (__subclasses__, __globals__, etc.)
        elif isinstance(node, ast.Attribute):
            attr_name = node.attr.lower()
            if attr_name in DISALLOWED_ATTRS or attr_name in DISALLOWED_NAMES:
                return False, f"Security Violation: Attribute access '{node.attr}' is restricted."

    return True, ""

def run_python_sandbox(code_str: str, timeout: float = 5.0) -> tuple[bool, str]:
    """
    Executes Python code in an isolated temporary directory with a clean environment.
    Returns (success_boolean, output_or_error_string).
    """
    if not code_str or not code_str.strip():
        return False, "No code provided to execute."

    # 1. Pre-execution static security validation
    is_safe, error_msg = validate_code_safety(code_str)
    if not is_safe:
        return False, f"⛔ {error_msg}"

    # 2. Run inside isolated temporary workspace with purged environment
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            solution_file = os.path.join(tmp_dir, "solution.py")
            with open(solution_file, "w", encoding="utf-8") as f:
                f.write(code_str)

            # Scrub sensitive environment variables (API keys, SMTP passwords)
            clean_env = {
                "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
                "PATH": os.environ.get("PATH", ""),
                "PYTHONPATH": "",
                "PYTHONIOENCODING": "utf-8"
            }

            res = subprocess.run(
                [sys.executable, "solution.py"],
                cwd=tmp_dir,
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            output = ""
            if res.stdout:
                output += res.stdout
            if res.stderr:
                output += res.stderr
            if not output:
                output = "Code executed successfully with no output."

            is_success = (res.returncode == 0)
            return is_success, output

    except subprocess.TimeoutExpired:
        return False, f"⏱️ TimeLimitExceeded: Code execution took longer than {timeout} seconds and was terminated."
    except Exception as e:
        return False, f"❌ Execution Error: {str(e)}"
