# Before running this script:
# pip install gradio openai
#
# Usage:
#   python chatbot.py prompt.md                     # Console mode, local code execution
#   python chatbot.py prompt.md --web               # Gradio web UI
#   python chatbot.py prompt.md --docker            # Use Docker sandbox for code execution
#   python chatbot.py prompt.md --debug             # Show tool calls/results inline
#   python chatbot.py prompt.md --show-reasoning    # Show model reasoning
#   python chatbot.py prompt.md --model gpt-5-mini  # Use a different model

import argparse
import asyncio
import io
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import gradio as gr
from openai import AsyncOpenAI, AuthenticationError

sys.path.insert(0, str(Path(__file__).parent.parent / "class_material"))
from tools import ToolBox
from usage import print_usage, format_usage_markdown

our_tools = ToolBox()


# ---------------------------------------------------------------------------
# Helper: human-in-the-loop approval gate
# ---------------------------------------------------------------------------

def approve_action(description: str) -> bool:
    """Prompt the user to approve a tool action. Returns True if approved."""
    print()
    print(' Approval Required '.center(40, '-'))
    print(description)
    print('-' * 40)
    response = input('Allow? [y/N] ')
    print()
    return response.lower() == 'y'


# Track whether we're running in web mode (approval bypassed)
_web_mode = False


# ===========================================================================
# Part 1: OpenAI's built-in tools
# ===========================================================================

# web_search is a built-in OpenAI tool — not registered via ToolBox.
# It gets added directly to the tools list sent to the API.
WEB_SEARCH_TOOL = {'type': 'web_search'}


# ===========================================================================
# Part 2: Real-world resources with human-in-the-loop
# ===========================================================================

from superbowldb import get_superbowl_info as _get_superbowl_info


@our_tools.tool
def get_superbowl_info(year: int) -> str:
    """Get Super Bowl information for a given year (2024-2025 supported).
    Returns structured data including winner, opponent, venue, and score.
    If data is not available for that year, returns a 'not found' result —
    you should then fall back to web_search."""
    if _web_mode or approve_action(f'Query Super Bowl database for year {year}'):
        result = _get_superbowl_info(year)
        return json.dumps(result, indent=2)
    return 'Action not approved by user. Ask them what they would like to do instead.'


@our_tools.tool
def get_current_time(format: str) -> str:
    """Get the current date and time. Format should be a Python strftime
    format string, e.g. '%Y-%m-%d %H:%M:%S' for full datetime or '%A' for
    day of the week."""
    if _web_mode or approve_action(f'Read system clock (format: {format})'):
        return datetime.now().strftime(format)
    return 'Action not approved by user. Ask them what they would like to do instead.'


# ===========================================================================
# Part 3: Code execution tool (registered conditionally in main)
# ===========================================================================

def _exec_python_local(code) -> tuple[str, str]:
    """Run Python code locally with captured stdout/stderr."""
    out_buffer = io.StringIO()
    err_buffer = io.StringIO()

    original_stdout = sys.stdout
    original_stderr = sys.stderr
    try:
        sys.stdout = out_buffer
        sys.stderr = err_buffer
        try:
            exec(code, {})
        except Exception:
            import traceback
            err_buffer.write(traceback.format_exc())
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
    return out_buffer.getvalue(), err_buffer.getvalue()


def exec_python(code: str) -> str:
    """Execute Python code. The code's STDOUT and STDERR are returned.
    Use this for calculations, data processing, random numbers, or any task
    you cannot reliably do on your own."""
    if _web_mode or approve_action(f'Run Python code:\n\n{code}'):
        stdout, stderr = _exec_python_local(code)
        parts = []
        if stdout:
            parts.append(f'STDOUT:\n{stdout}')
        if stderr:
            parts.append(f'STDERR:\n{stderr}')
        return '\n'.join(parts) if parts else '(no output)'
    return 'Code was not approved by user. Discuss an alternative with them.'


def exec_python_docker(code: str, timeout: int) -> str:
    """Execute Python code inside a secure Docker sandbox.
    The code runs in an isolated container with no network access,
    limited CPU/memory, and a read-only filesystem. STDOUT and STDERR
    are returned as JSON. Use this for calculations, data processing,
    or any task you cannot reliably do on your own.
        code: the Python code to execute
        timeout: max seconds the code can run before termination"""
    from codebot import execute_code
    result = execute_code(code, timeout)
    return json.dumps(result, indent=2)


def register_code_tool(docker_mode: bool):
    """Register the appropriate code execution tool based on mode."""
    if docker_mode:
        our_tools.tool(exec_python_docker)
    else:
        our_tools.tool(exec_python)


# ===========================================================================
# Utilities
# ===========================================================================

def sanitize_input(text: str) -> str:
    """Remove invalid Unicode surrogates from user input."""
    return text.encode('utf-8', errors='replace').decode('utf-8')


# ===========================================================================
# ChatAgent
# ===========================================================================

class ChatAgent:
    def __init__(self, model: str, prompt: str, show_reasoning: bool,
                 reasoning_effort: str | None, debug: bool = False):
        self._ai = AsyncOpenAI()
        self.model = model
        self.show_reasoning = show_reasoning
        self.debug = debug
        self.reasoning = {}
        if show_reasoning:
            self.reasoning['summary'] = 'auto'
        if 'gpt-5' in self.model and reasoning_effort:
            self.reasoning['effort'] = reasoning_effort

        self.usage = []
        self.usage_markdown = format_usage_markdown(self.model, [])

        self._history = []
        self._prompt = prompt
        if prompt:
            self._history.append({'role': 'system', 'content': prompt})

        self.total_response_time = 0.0
        self.response_count = 0

    async def get_response(self, user_message: str):
        self._history.append({'role': 'user', 'content': user_message})

        all_tools = our_tools.tools + [WEB_SEARCH_TOOL]

        while True:
            start_time = time.time()

            # Retry up to 3 times on transient auth errors (OpenAI occasionally
            # returns 401 even with a valid key)
            for attempt in range(3):
                try:
                    response = await self._ai.responses.create(
                        input=self._history,
                        model=self.model,
                        reasoning=self.reasoning,
                        tools=all_tools,
                    )
                    break
                except AuthenticationError:
                    if attempt < 2:
                        wait = 2 ** attempt
                        print(f'\n[retry] OpenAI returned 401, retrying in {wait}s '
                              f'(attempt {attempt + 2}/3)...', file=sys.stderr)
                        await asyncio.sleep(wait)
                    else:
                        raise

            elapsed = time.time() - start_time
            self.total_response_time += elapsed
            self.response_count += 1

            self.usage.append(response.usage)
            self.usage_markdown = format_usage_markdown(self.model, self.usage)
            self._history.extend(response.output)

            has_tool_call = False

            for item in response.output:
                if item.type == 'reasoning':
                    for chunk in item.summary:
                        yield 'reasoning', chunk.text

                elif item.type == 'function_call':
                    has_tool_call = True
                    call_text = f'{item.name}({item.arguments})'
                    yield 'reasoning', call_text
                    if self.debug:
                        yield 'output', f'\n[tool call] {call_text}\n'

                    func = our_tools.get_tool_function(item.name)
                    args = json.loads(item.arguments)
                    result = func(**args)
                    self._history.append({
                        'type': 'function_call_output',
                        'call_id': item.call_id,
                        'output': str(result),
                    })
                    yield 'reasoning', str(result)
                    if self.debug:
                        yield 'output', f'[tool result] {result}\n'

                elif item.type == 'web_search_call':
                    has_tool_call = True
                    try:
                        query = item.action.query
                    except AttributeError:
                        query = ''
                    yield 'reasoning', f'web_search("{query}")'
                    if self.debug:
                        yield 'output', f'\n[web_search] "{query}"\n'

                elif item.type == 'message':
                    for chunk in item.content:
                        yield 'output', chunk.text
                    return

            if not has_tool_call:
                return

    def _format_timer(self) -> str:
        if self.response_count == 0:
            return ""
        avg_time = self.total_response_time / self.response_count
        return (
            f"\n\n**Total response time**: {self.total_response_time:.2f} seconds "
            f"({self.response_count} responses, avg {avg_time:.2f} seconds/response)"
        )

    def _get_message_info(self, msg):
        if isinstance(msg, dict):
            return msg.get('role'), msg.get('content', '')
        return getattr(msg, 'role', None), getattr(msg, 'content', '')

    def save_chat(self) -> str:
        timestamp = datetime.now().strftime("%H-%M-%S")
        filename = f"chat_{timestamp}.md"

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_count = len([msg for msg in self._history
                             if self._get_message_info(msg)[0] in ['user', 'assistant']])

        parts = []
        parts.append("# Chat Session\n")
        parts.append(f"**Model**: {self.model}\n")
        parts.append(f"**Saved**: {now_str}\n")
        parts.append(f"**Messages**: {message_count}\n")

        if self.reasoning.get('effort'):
            parts.append(f"**Reasoning effort**: {self.reasoning['effort']}\n")

        system_messages = [msg for msg in self._history
                           if self._get_message_info(msg)[0] == 'system']
        if system_messages:
            parts.append("\n## System Prompt\n\n")
            _, content = self._get_message_info(system_messages[0])
            parts.append(content)
            parts.append("\n")

        parts.append("\n## Conversation\n")
        for msg in self._history:
            if isinstance(msg, dict):
                role = msg.get('role')
                if role == 'user':
                    parts.append(f"\n**User**: {msg['content']}\n")
                elif role == 'assistant':
                    parts.append(f"\n**Assistant**: {msg['content']}\n")
                elif msg.get('type') == 'function_call_output':
                    parts.append(f"\n> **Tool Result** (`{msg.get('call_id', '')}`): {msg['output']}\n")
                continue

            item_type = getattr(msg, 'type', None)
            if item_type == 'function_call':
                parts.append(f"\n> **Tool Call**: `{msg.name}({msg.arguments})`\n")
            elif item_type == 'web_search_call':
                query = getattr(getattr(msg, 'action', None), 'query', '')
                parts.append(f"\n> **Web Search**: `{query}`\n")
            elif item_type == 'message':
                content = '\n'.join(chunk.text for chunk in msg.content)
                parts.append(f"\n**Assistant**: {content}\n")

        if self.usage:
            parts.append("\n## Usage Statistics\n\n")
            parts.append(format_usage_markdown(self.model, self.usage))
            parts.append(self._format_timer())

        with open(filename, 'w', encoding='utf-8', errors='replace') as f:
            f.write(''.join(parts))

        return filename

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print_usage(self.model, self.usage)
        if self.response_count > 0:
            avg_time = self.total_response_time / self.response_count
            print(f'Total response time: {self.total_response_time:.2f} seconds '
                  f'({self.response_count} responses, avg {avg_time:.2f} seconds/response)',
                  file=sys.stderr)


# ===========================================================================
# Console mode
# ===========================================================================

async def _main_console(agent_args):
    with ChatAgent(**agent_args) as agent:
        print("Toolbot 2e — type /save to save, /exit to quit, or press Enter to quit.\n")
        while True:
            message = input('User: ')
            if not message:
                break
            message = sanitize_input(message)
            if message == '/save':
                filename = agent.save_chat()
                print(f'Chat saved to: {filename}\n')
                continue
            if message == '/exit':
                print('Goodbye!')
                break

            reasoning_complete = True
            if agent.show_reasoning:
                print(' Reasoning '.center(30, '-'))
                reasoning_complete = False

            async for text_type, text in agent.get_response(message):
                if text_type == 'output' and not reasoning_complete:
                    print()
                    print('-' * 30)
                    print()
                    print('Agent: ', end='')
                    reasoning_complete = True

                print(text, end='', flush=True)
            print()
            print()


# ===========================================================================
# Gradio web mode
# ===========================================================================

def _main_gradio(agent_args):
    css = """
    .gradio-container, .gradio-app, .gradio-root {
      width: 120ch;
      max-width: 120ch !important;
      margin-left: auto !important;
      margin-right: auto !important;
      box-sizing: border-box !important;
    }

    #reasoning-md {
        max-height: 300px;
        overflow-y: auto;
    }
    """

    reasoning_view = gr.Markdown('', elem_id='reasoning-md')
    usage_view = gr.Markdown('')

    with gr.Blocks(css=css, theme=gr.themes.Monochrome()) as demo:
        agent = gr.State()

        async def get_response(message, chat_view_history, agent):
            message = sanitize_input(message)
            if message == '/save':
                filename = agent.save_chat()
                response = f'Chat saved to: {filename}'
                yield response, '', agent.usage_markdown + agent._format_timer(), agent
                return

            output = ""
            reasoning = ""

            async for text_type, text in agent.get_response(message):
                if text_type == 'reasoning':
                    reasoning += text
                elif text_type == 'output':
                    output += text
                else:
                    raise NotImplementedError(text_type)

                yield output, reasoning, agent.usage_markdown + agent._format_timer(), agent

            yield output, reasoning, agent.usage_markdown + agent._format_timer(), agent

        with gr.Row():
            with gr.Column(scale=5):
                bot = gr.Chatbot(
                    label=' ',
                    height=600,
                    resizable=True,
                )
                chat = gr.ChatInterface(
                    chatbot=bot,
                    fn=get_response,
                    additional_inputs=[agent],
                    additional_outputs=[reasoning_view, usage_view, agent],
                )

            with gr.Column(scale=1):
                reasoning_view.render()
                usage_view.render()

        demo.load(fn=lambda: ChatAgent(**agent_args), outputs=[agent])

    demo.launch()


# ===========================================================================
# Entry point
# ===========================================================================

def main(prompt_path: Path, model: str, show_reasoning: bool,
         reasoning_effort: str | None, use_web: bool, debug: bool,
         docker: bool):
    global _web_mode

    # Register the code execution tool based on mode
    register_code_tool(docker_mode=docker)

    if use_web:
        _web_mode = True
        print("NOTE: Running in web mode — human-in-the-loop approval is bypassed.",
              file=sys.stderr)

    agent_args = dict(
        model=model,
        prompt=prompt_path.read_text() if prompt_path else '',
        show_reasoning=show_reasoning,
        reasoning_effort=reasoning_effort,
        debug=debug,
    )

    if use_web:
        _main_gradio(agent_args)
    else:
        asyncio.run(_main_console(agent_args))


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Toolbot 2e')
    parser.add_argument('prompt_file', nargs='?', type=Path, default=None)
    parser.add_argument('--web', action='store_true',
                        help='Launch Gradio web UI')
    parser.add_argument('--model', default='gpt-5-nano',
                        help='OpenAI model to use (default: gpt-5-nano)')
    parser.add_argument('--show-reasoning', action='store_true',
                        help='Display model reasoning')
    parser.add_argument('--reasoning-effort', default='low',
                        help='Reasoning effort level (low/medium/high)')
    parser.add_argument('--debug', action='store_true',
                        help='Show tool calls and results inline')
    parser.add_argument('--docker', action='store_true',
                        help='Use Docker sandbox for code execution '
                             '(requires: docker build -t safe-container:latest '
                             'in class_material/docker/)')
    args = parser.parse_args()
    main(args.prompt_file, args.model, args.show_reasoning,
         args.reasoning_effort, args.web, args.debug, args.docker)
