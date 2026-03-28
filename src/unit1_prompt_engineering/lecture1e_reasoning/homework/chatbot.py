# Before running this script:
# pip install gradio openai

import argparse
import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path

import gradio as gr
from openai import AsyncOpenAI

# Add class_material directory to Python path for imports
class_material_dir = Path(__file__).parent.parent / "class_material"
sys.path.insert(0, str(class_material_dir))

from usage import print_usage, format_usage_markdown


def sanitize_input(text: str) -> str:
    """Remove invalid Unicode surrogates from user input.

    This handles terminal encoding issues where Greek characters
    may be read with surrogate errors.
    """
    return text.encode('utf-8', errors='replace').decode('utf-8')


class ChatAgent:
    def __init__(self, model: str, prompt: str, show_reasoning: bool, reasoning_effort: str | None):
        self._ai = AsyncOpenAI()
        self.usage = []
        self.model = model
        self.show_reasoning = show_reasoning
        self.reasoning = {}
        if show_reasoning:
            self.reasoning['summary'] = 'auto'
        if 'gpt-5' in self.model and reasoning_effort:
            self.reasoning['effort'] = reasoning_effort
        self._prompt = prompt
        self._history = []
        if prompt:
            self._history.append({'role': 'system', 'content': prompt})

        # Timer tracking
        self.total_response_time = 0.0
        self.response_count = 0

    async def get_response(self, user_message: str):
        self._history.append({'role': 'user', 'content': user_message})

        start_time = time.time()
        stream = self._ai.responses.stream(
            input=self._history,
            model=self.model,
            reasoning=self.reasoning,
        )
        async with stream as stream:
            async for event in stream:
                if event.type == "response.output_text.delta":
                    yield 'output', event.delta

                if event.type == "response.reasoning_summary_text.delta":
                    yield 'reasoning', event.delta

            response = await stream.get_final_response()
            elapsed = time.time() - start_time
            self.total_response_time += elapsed
            self.response_count += 1
            self.usage.append(response.usage)
            self._history.extend(
                response.output
            )

    def _format_timer(self) -> str:
        """Format timer information as markdown."""
        if self.response_count == 0:
            return ""
        avg_time = self.total_response_time / self.response_count
        return (
            f"\n\n**Total response time**: {self.total_response_time:.2f} seconds "
            f"({self.response_count} responses, avg {avg_time:.2f} seconds/response)"
        )

    def _get_message_info(self, msg):
        """Extract role and content from message (dict or response object)."""
        if isinstance(msg, dict):
            return msg.get('role'), msg.get('content', '')
        else:
            # Response object - use attribute access
            return getattr(msg, 'role', None), getattr(msg, 'content', '')

    def save_chat(self) -> str:
        """Save the current chat history to a markdown file.

        Returns:
            The filename of the saved chat.
        """
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%H-%M-%S")
        filename = f"chat_{timestamp}.md"

        # Build markdown content
        content_parts = []

        # Header with metadata
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_count = len([msg for msg in self._history
                             if self._get_message_info(msg)[0] in ['user', 'assistant']])

        content_parts.append("# Chat Session\n")
        content_parts.append(f"**Model**: {self.model}\n")
        content_parts.append(f"**Saved**: {now_str}\n")
        content_parts.append(f"**Messages**: {message_count}\n")

        # Add reasoning configuration info
        if self.reasoning.get('effort'):
            content_parts.append(f"**Reasoning enabled**: Yes\n")
            content_parts.append(f"**Reasoning effort**: {self.reasoning['effort']}\n")
            if self.show_reasoning:
                content_parts.append(f"**Reasoning display**: Enabled (shown in console/UI)\n")
            else:
                content_parts.append(f"**Reasoning display**: Disabled (not shown to user)\n")
        else:
            content_parts.append(f"**Reasoning enabled**: No\n")

        # System prompt section
        system_messages = [msg for msg in self._history
                           if self._get_message_info(msg)[0] == 'system']
        if system_messages:
            content_parts.append("\n## System Prompt\n\n")
            _, content = self._get_message_info(system_messages[0])
            content_parts.append(content)
            content_parts.append("\n")

        # Conversation section
        content_parts.append("\n## Conversation\n")
        for msg in self._history:
            role, content = self._get_message_info(msg)
            if role == 'user':
                content_parts.append(f"\n**User**: {content}\n")
            elif role == 'assistant':
                content_parts.append(f"\n**Assistant**: {content}\n")

        # Usage statistics section
        if self.usage:
            content_parts.append("\n## Usage Statistics\n\n")
            content_parts.append(format_usage_markdown(self.model, self.usage))
            content_parts.append(self._format_timer())

        # Write to file
        with open(filename, 'w', encoding='utf-8', errors='replace') as f:
            f.write(''.join(content_parts))

        return filename

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print_usage(self.model, self.usage)
        if self.response_count > 0:
            avg_time = self.total_response_time / self.response_count
            print(f'Total response time: {self.total_response_time:.2f} seconds ({self.response_count} responses, avg {avg_time:.2f} seconds/response)', file=sys.stderr)


async def _main_console(agent):
    while True:
        message = input('User: ')
        if not message:
            break
        # Sanitize input to handle terminal encoding issues
        message = sanitize_input(message)
        if message == '/save':
            filename = agent.save_chat()
            print(f'Chat saved to: {filename}')
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
                print('Agent: ')
                reasoning_complete = True

            print(text, end='', flush=True)
        print()
        print()


def _main_gradio(agent):
    # Constrain width with CSS and center
    css = """
    /* limit overall Gradio app width and center it */
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
    usage_view = gr.Markdown(format_usage_markdown(agent.model, []) + agent._format_timer())

    with gr.Blocks(css=css, theme=gr.themes.Monochrome()) as demo:
        async def get_response(message, chat_view_history):
            # Sanitize input to handle encoding issues
            message = sanitize_input(message)
            if message == '/save':
                filename = agent.save_chat()
                response = f'Chat saved to: {filename}'
                usage_content = format_usage_markdown(agent.model, agent.usage) + agent._format_timer()
                yield response, '', usage_content
                return  # Early exit after /save

            output = ""
            reasoning = ""

            async for text_type, text in agent.get_response(message):
                if text_type == 'reasoning':
                    reasoning += text
                elif text_type == 'output':
                    output += text
                else:
                    raise NotImplementedError(text_type)

                usage_content = format_usage_markdown(agent.model, agent.usage) + agent._format_timer()
                yield output, reasoning, usage_content

            usage_content = format_usage_markdown(agent.model, agent.usage) + agent._format_timer()
            yield output, reasoning, usage_content

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
                    additional_outputs=[reasoning_view, usage_view]
                )

            with gr.Column(scale=1):
                reasoning_view.render()
                usage_view.render()

    demo.launch()


def main(prompt_path: Path, model: str, show_reasoning: bool, reasoning_effort: str | None, use_web: bool):
    with ChatAgent(model, prompt_path.read_text() if prompt_path else '', show_reasoning, reasoning_effort) as agent:
        if use_web:
            _main_gradio(agent)
        else:
            asyncio.run(_main_console(agent))


# Launch app
if __name__ == "__main__":
    parser = argparse.ArgumentParser('ChatBot')
    parser.add_argument('prompt_file', nargs='?', type=Path, default=None)
    parser.add_argument('--web', action='store_true')
    parser.add_argument('--model', default='gpt-5-nano')
    parser.add_argument('--show-reasoning', action='store_true')
    parser.add_argument('--reasoning-effort', default='low')
    args = parser.parse_args()
    main(args.prompt_file, args.model, args.show_reasoning, args.reasoning_effort, args.web)
