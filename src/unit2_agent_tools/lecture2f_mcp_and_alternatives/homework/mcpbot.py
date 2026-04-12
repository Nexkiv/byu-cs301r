# Before running this script:
# pip install gradio openai

import argparse
import asyncio
import io
import json
import sys
from datetime import datetime
from pathlib import Path

import gradio as gr
from openai import AsyncOpenAI

from tools import ToolBox
from usage import print_usage, format_usage_markdown

our_tools = ToolBox()
_web_mode = False


# --- Local tools ---

def _exec_python(code: str) -> str:
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

    stdout = out_buffer.getvalue()
    stderr = err_buffer.getvalue()
    parts = []
    if stdout:
        parts.append(f"stdout:\n{stdout}")
    if stderr:
        parts.append(f"stderr:\n{stderr}")
    return '\n'.join(parts) if parts else '(no output)'


def exec_python(code: str) -> str:
    """Execute the provided python code. STDOUT and STDERR are returned."""
    if not _web_mode:
        print()
        print(' Agent Code '.center(40, '-'))
        print(code)
        print('-' * 40)
        response = input('Allow? [y/N] ')
        if response.lower() != 'y':
            return 'This code was not approved by the user. Discuss with them an alternative.'

    return _exec_python(code)


# --- MCP helpers ---

def build_mcp_tools(mcp_args: list[str] | None) -> list[dict]:
    if not mcp_args:
        return []
    tools = []
    for spec in mcp_args:
        label, url = spec.split('=', 1)
        tools.append({
            "type": "mcp",
            "server_label": label,
            "server_url": url,
            "require_approval": "never",
        })
    return tools


# --- Chat agent ---

class ChatAgent:
    def __init__(self, model: str, prompt: str, show_reasoning: bool, reasoning_effort: str | None):
        self._ai = AsyncOpenAI()
        self.model = model
        self.show_reasoning = show_reasoning
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

    def _get_message_info(self, msg):
        if isinstance(msg, dict):
            return msg.get('role'), msg.get('content', '')
        return getattr(msg, 'role', None), getattr(msg, 'content', '')

    def save_chat(self) -> str:
        timestamp = datetime.now().strftime("%H-%M-%S")
        filename = f"chat_{timestamp}.md"

        parts = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_count = len([m for m in self._history
                             if self._get_message_info(m)[0] in ['user', 'assistant']])

        parts.append("# Chat Session\n")
        parts.append(f"**Model**: {self.model}\n")
        parts.append(f"**Saved**: {now_str}\n")
        parts.append(f"**Messages**: {message_count}\n")

        system_messages = [m for m in self._history
                           if self._get_message_info(m)[0] == 'system']
        if system_messages:
            parts.append("\n## System Prompt\n\n")
            _, content = self._get_message_info(system_messages[0])
            parts.append(content)
            parts.append("\n")

        parts.append("\n## Conversation\n")
        for msg in self._history:
            # Dict-based entries (user messages, system, function_call_output)
            if isinstance(msg, dict):
                role = msg.get('role') or msg.get('type', '')
                if role == 'user':
                    parts.append(f"\n**User**: {msg.get('content', '')}\n")
                elif role == 'function_call_output':
                    parts.append(f"\n> **Tool Result** (`{msg.get('call_id', '')}`):\n> ```\n> {msg.get('output', '')}\n> ```\n")
                continue

            # Response output items (assistant messages, function calls, reasoning)
            item_type = getattr(msg, 'type', None)
            if item_type == 'message':
                text = ''.join(c.text for c in msg.content if hasattr(c, 'text'))
                if text:
                    parts.append(f"\n**Assistant**: {text}\n")
            elif item_type == 'function_call':
                parts.append(f"\n**Tool Call**: `{msg.name}({msg.arguments})`\n")

        if self.usage:
            parts.append("\n## Usage Statistics\n\n")
            parts.append(format_usage_markdown(self.model, self.usage))

        with open(filename, 'w', encoding='utf-8', errors='replace') as f:
            f.write(''.join(parts))

        return filename

    async def get_response(self, user_message: str):
        self._history.append({'role': 'user', 'content': user_message})

        while True:
            response = await self._ai.responses.create(
                input=self._history,
                model=self.model,
                reasoning=self.reasoning,
                tools=our_tools.tools
            )

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
                    yield 'reasoning', f'{item.name}({item.arguments})'

                    func = our_tools.get_tool_function(item.name)
                    args = json.loads(item.arguments)
                    result = func(**args)
                    self._history.append({
                        'type': 'function_call_output',
                        'call_id': item.call_id,
                        'output': str(result)
                    })
                    yield 'reasoning', str(result)

                elif item.type == 'message':
                    for chunk in item.content:
                        yield 'output', chunk.text
                    return

            if not has_tool_call:
                return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print_usage(self.model, self.usage)


# --- Console mode ---

async def _main_console(agent_args):
    with ChatAgent(**agent_args) as agent:
        while True:
            message = input('User: ')
            if not message:
                break
            if message == '/exit':
                print('Goodbye!')
                break
            if message == '/save':
                filename = agent.save_chat()
                print(f'Chat saved to: {filename}')
                continue

            reasoning_complete = True
            if agent.show_reasoning:
                print(' Reasoning '.center(30, '-'))
                reasoning_complete = False

            last_type = ''
            async for text_type, text in agent.get_response(message):
                if text_type == 'output' and not reasoning_complete:
                    print()
                    print('-' * 30)
                    print()
                    print('Agent: ')
                    reasoning_complete = True

                if last_type != text_type:
                    print(f'\n{text_type}: ', end='', flush=True)
                    last_type = text_type

                print(text, end='', flush=True)
            print()
            print()


# --- Gradio web mode ---

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
            if message == '/save':
                filename = agent.save_chat()
                yield f'Chat saved to: {filename}', '', agent.usage_markdown, agent
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

                yield output, reasoning, agent.usage_markdown, agent

            yield output, reasoning, agent.usage_markdown, agent

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
                    additional_outputs=[reasoning_view, usage_view, agent]
                )

            with gr.Column(scale=1):
                reasoning_view.render()
                usage_view.render()

        demo.load(fn=lambda: ChatAgent(**agent_args), outputs=[agent])

    demo.launch()


# --- Entry point ---

def main(prompt_path: Path, model: str, show_reasoning, reasoning_effort: str | None, use_web: bool, mcp_specs: list[str], enable_exec: bool):
    global _web_mode
    _web_mode = use_web

    if enable_exec:
        our_tools.tool(exec_python)

    our_tools.tools += build_mcp_tools(mcp_specs)

    agent_args = dict(
        model=model,
        prompt=prompt_path.read_text() if prompt_path else '',
        show_reasoning=show_reasoning,
        reasoning_effort=reasoning_effort,
    )

    if use_web:
        _main_gradio(agent_args)
    else:
        asyncio.run(_main_console(agent_args))


if __name__ == "__main__":
    parser = argparse.ArgumentParser('MCP ChatBot')
    parser.add_argument('prompt_file', nargs='?', type=Path, default=None)
    parser.add_argument('--web', action='store_true')
    parser.add_argument('--model', default='gpt-5-nano')
    parser.add_argument('--show-reasoning', action='store_true')
    parser.add_argument('--reasoning-effort', default='low')
    parser.add_argument('--mcp', nargs='*', default=[], help='MCP servers as label=url pairs (e.g. stocks=https://127.0.0.1:8000/mcp)')
    parser.add_argument('--exec-python', action='store_true', help='Enable the exec_python tool')
    args = parser.parse_args()
    main(args.prompt_file, args.model, args.show_reasoning, args.reasoning_effort, args.web, args.mcp, args.exec_python)
