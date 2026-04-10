# Before running this script:
# pip install gradio openai

import argparse
import asyncio
import json
import math
import random
import sys
import time
from datetime import datetime, date
from pathlib import Path

import gradio as gr
from openai import AsyncOpenAI

sys.path.insert(0, str(Path(__file__).parent.parent / "class_material"))
from usage import print_usage, format_usage_markdown

from tools import ToolBox

our_tools = ToolBox()


@our_tools.tool
def get_random_number(lower: int, upper: int) -> int:
    """Get a random integer between lower and upper (inclusive)."""
    return random.randint(lower, upper)


@our_tools.tool
def is_prime(n: int) -> str:
    """Test if any integer (including very large numbers) is prime using Fermat's primality test. Always use this tool instead of web search for primality questions."""
    if n < 2:
        return f"{n} is not prime"
    if n < 4:
        return f"{n} is prime"
    if n % 2 == 0:
        return f"{n} is not prime (even)"
    for _ in range(10):
        a = random.randrange(2, n)
        if pow(a, n - 1, n) != 1:
            return f"{n} is composite (Fermat witness: {a})"
    return f"{n} is probably prime (passed 10 Fermat tests)"


@our_tools.tool
def subset_ratio(subset_size: int, set_size: int) -> str:
    """Calculate a ratio or percentage. Use this whenever asked about ratios, percentages, fractions, or proportions between two quantities."""
    if set_size == 0:
        return "Error: set size cannot be zero"
    pct = (subset_size / set_size) * 100
    return f"{subset_size}/{set_size} = {pct:.2f}%"


@our_tools.tool
def days_between(date1: str, date2: str) -> str:
    """Calculate the exact number of days between two dates (YYYY-MM-DD format)."""
    d1 = date.fromisoformat(date1)
    d2 = date.fromisoformat(date2)
    delta = abs((d2 - d1).days)
    return f"{delta} days between {date1} and {date2}"


@our_tools.tool
def count_characters(text: str) -> int:
    """Count the exact number of characters in a string."""
    return len(text)


# Built-in web_search tool (handled by OpenAI, not locally)
WEB_SEARCH_TOOL = {'type': 'web_search'}


def sanitize_input(text: str) -> str:
    """Remove invalid Unicode surrogates from user input."""
    return text.encode('utf-8', errors='replace').decode('utf-8')


class ChatAgent:
    def __init__(self, model: str, prompt: str, show_reasoning: bool, reasoning_effort: str | None,
                 debug: bool = False):
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
            response = await self._ai.responses.create(
                input=self._history,
                model=self.model,
                reasoning=self.reasoning,
                tools=all_tools,
            )
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
            # Dict-based entries (system, user, function_call_output)
            if isinstance(msg, dict):
                role = msg.get('role')
                if role == 'user':
                    parts.append(f"\n**User**: {msg['content']}\n")
                elif role == 'assistant':
                    parts.append(f"\n**Assistant**: {msg['content']}\n")
                elif msg.get('type') == 'function_call_output':
                    parts.append(f"\n> **Tool Result** (`{msg.get('call_id', '')}`): {msg['output']}\n")
                continue

            # Response output items (function_call, message, web_search_call, etc.)
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


async def _main_console(agent_args):
    with ChatAgent(**agent_args) as agent:
        print("Toolbot — type /save to save, /exit to quit, or press Enter to quit.\n")
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


def main(prompt_path: Path, model: str, show_reasoning: bool, reasoning_effort: str | None, use_web: bool, debug: bool):
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
    parser = argparse.ArgumentParser('Toolbot')
    parser.add_argument('prompt_file', nargs='?', type=Path, default=None)
    parser.add_argument('--web', action='store_true')
    parser.add_argument('--model', default='gpt-5-nano')
    parser.add_argument('--show-reasoning', action='store_true')
    parser.add_argument('--reasoning-effort', default='low')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    main(args.prompt_file, args.model, args.show_reasoning, args.reasoning_effort, args.web, args.debug)
