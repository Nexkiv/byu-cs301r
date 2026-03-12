import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

import yaml
from openai import AsyncOpenAI

# Add class_material directory to Python path for imports
class_material_dir = Path(__file__).parent.parent / "class_material"
sys.path.insert(0, str(class_material_dir))

from run_agent import run_agent, as_tool, conclude, current_agent
from tools import ToolBox
from usage import print_usage

LOG_FORMAT = '%(filename)-10.10s %(levelname)-4.4s %(asctime)s %(message)s'

toolbox = ToolBox()
toolbox.tool(conclude)


@toolbox.tool
def message_user(message: str):
    """
    Display a message to the user without waiting for input.
    Use this to show responses, information, or status messages.
    :param message: The message to display to the user.
    """
    _agent = current_agent.get()
    name = _agent['name'] if _agent else 'Agent'
    print(f'{name}: {message}')


@toolbox.tool
def query_user(message: str):
    """
    Display a message and wait for user input.
    Use this when you need the user to provide input or answer a question.
    :param message: The message/question to display to the user.
    :return: The user's response.
    """
    _agent = current_agent.get()
    name = _agent['name'] if _agent else 'Agent'
    print(f'{name}: {message}')
    return input('User: ')


async def main(agent_config: Path):
    """
    Main async function that orchestrates the chat system with guardrails.

    :param agent_config: Path to the YAML configuration file
    """
    client = AsyncOpenAI()
    usages = []  # Shared usage tracking across all agent calls

    try:
        def add_to_toolbox(_agent):
            """Register non-main agents as tools"""
            toolbox.tool(as_tool(client, toolbox, _agent, usage=usages))

        # Load all agents from YAML
        agents = list(yaml.safe_load_all(agent_config.read_text()))

        # Register all non-main agents as tools
        for agent in agents:
            if agent['name'] == 'main':
                continue
            add_to_toolbox(agent)

        # Get the main agent
        main_agent = next(agent for agent in agents if agent['name'] == 'main')

        # Run the main agent (it will handle the chat loop)
        response = await run_agent(
            client, toolbox, main_agent,
            user_message=None,  # No initial message - main agent starts conversation
            usage=usages
        )

        # Print final response if any (main agent might conclude without output)
        if response:
            print(response)
            print()

    finally:
        # Always print usage statistics, even if interrupted
        if usages:
            print("\n" + "=" * 50)
            print("Token Usage Summary")
            print("=" * 50)
            print_usage(usages)


def _configure_logging(debug: bool) -> None:
    """Configure logging with optional debug mode"""
    local_level = logging.DEBUG if debug else logging.INFO
    use_dark_gray = (
            sys.stderr.isatty()
            and os.getenv('NO_COLOR') is None
            and os.getenv('TERM', '').lower() != 'dumb'
    )
    format_string = f'\x1b[90m{LOG_FORMAT}\x1b[0m' if use_dark_gray else LOG_FORMAT
    logging.basicConfig(
        level=logging.WARNING,
        format=format_string,
        datefmt='%H:%M:%S',
        force=True,
    )
    for logger_name in ('__main__', 'censor', 'run_agent', 'tools', 'usage'):
        logging.getLogger(logger_name).setLevel(local_level)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Chat system with input and output guardrails'
    )
    parser.add_argument(
        'agent_config',
        type=Path,
        nargs='?',
        default=Path('censor.yaml'),
        help='Path to agent configuration YAML file (default: censor.yaml)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    args = parser.parse_args()

    _configure_logging(args.debug)

    # Keyboard interrupt handling
    try:
        asyncio.run(main(args.agent_config))
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
