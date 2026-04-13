import argparse
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

import yaml
from openai import AsyncOpenAI

from graph_memory import GraphMemory
from memory import MemoryManager
from run_agent import run_agent, conclude, current_agent, current_memory
from tools import ToolBox
from usage import print_usage

LOG_FORMAT = '%(filename)-10.10s %(levelname)-4.4s %(asctime)s %(message)s'

graph = GraphMemory()
toolbox = ToolBox()
# Transcript entries: each is a dict with 'type' and relevant fields
# Types: 'user', 'assistant', 'tool_call', 'tool_result'
transcript: list[dict] = []
toolbox.tool(conclude)

# Wrap toolbox.run_tool to capture tool calls and results
_original_run_tool = toolbox.run_tool


async def _logging_run_tool(tool_name: str, **kwargs):
    transcript.append({
        'type': 'tool_call',
        'name': tool_name,
        'arguments': kwargs,
    })
    result = await _original_run_tool(tool_name, **kwargs)
    transcript.append({
        'type': 'tool_result',
        'name': tool_name,
        'output': str(result) if result is not None else '(none)',
    })
    return result


toolbox.run_tool = _logging_run_tool


# --- MemGPT memory tools (from class material) ---

def _require_memory():
    memory = current_memory.get()
    if not memory or not memory.enabled:
        raise RuntimeError('Memory is not enabled for the current agent.')
    return memory


@toolbox.tool
def talk_to_user(message: str) -> str:
    """
    Use this function to communicate with the user.
    All communication to and from the user MUST go through this tool.
    :param message: The message to send to the user.
    :return: The user's response.
    """
    _agent = current_agent.get()
    name = _agent['name'] if _agent else 'Agent'
    print(f'\n{name}: {message}')
    # talk_to_user is already captured by the run_tool wrapper,
    # but we also add explicit assistant/user entries for readability
    transcript.append({'type': 'assistant', 'name': name, 'content': message})
    user_input = input('\nUser: ')

    if user_input.startswith('/'):
        result = _handle_slash_command(user_input)
        if result is None:
            # /exit was called
            graph.save()
            print_usage(usages)
            sys.exit(0)
        print(f'\n{result}')
        return f'[Slash command result]\n{result}'

    transcript.append({'type': 'user', 'content': user_input})
    return user_input


@toolbox.tool
def append_core_memory(section: str, content: str) -> str:
    """
    Append durable information to core memory.
    :param section: The core memory section to update: persona or user.
    :param content: The text to append.
    :return: A status message.
    """
    return _require_memory().append_core_memory(section, content)


@toolbox.tool
def replace_core_memory(section: str, content: str) -> str:
    """
    Replace a core memory section.
    :param section: The core memory section to replace: persona or user.
    :param content: The new text for the section.
    :return: A status message.
    """
    return _require_memory().replace_core_memory(section, content)


@toolbox.tool
def search_recall_memory(query: str, limit: int, offset: int | None = None) -> str:
    """
    Search chat and tool history stored in recall memory.
    :param query: Search text.
    :param limit: Number of results to return.
    :param offset: Pagination offset.
    :return: Formatted search results.
    """
    memory = _require_memory()
    results = memory.search_recall_memory(query, limit=limit, offset=offset or 0)
    return memory.format_search_results('Recall memory', query, results, 'text')


@toolbox.tool
def show_memory_status() -> str:
    """
    Show token budgets and current memory usage.
    :return: Memory status text.
    """
    memory = _require_memory()
    status = memory.status(current_agent.get().get('prompt'))
    graph_stats = f'\ngraph_nodes={len(graph._nodes)}\ngraph_edges={len(graph._edges)}'
    return status + graph_stats


# --- Graph memory tools ---

@toolbox.tool
def add_node(label: str, node_type: str, description: str) -> str:
    """
    Add or update a concept node in the knowledge graph.
    :param label: Display name for the concept (e.g. "Medici Family").
    :param node_type: Category: person, place, event, idea, era, or organization.
    :param description: Brief description of this concept.
    :return: Status message with the node ID.
    """
    return graph.add_node(label, node_type, description)


@toolbox.tool
def add_edge(source: str, target: str, relationship: str, context: str) -> str:
    """
    Add a relationship edge between two existing nodes in the knowledge graph.
    :param source: Label or ID of the source node.
    :param target: Label or ID of the target node.
    :param relationship: Name of the relationship (e.g. "financed", "traded with").
    :param context: Brief explanation of this connection.
    :return: Status message.
    """
    return graph.add_edge(source, target, relationship, context)


@toolbox.tool
def get_connections(node_id: str, depth: int = 1) -> str:
    """
    Get all connections for a node, expanding outward by depth levels.
    :param node_id: The node label or ID to explore from.
    :param depth: How many hops to traverse (1 = immediate neighbors, 2 = neighbors of neighbors).
    :return: Formatted connection tree.
    """
    return graph.get_connections(node_id, depth)


@toolbox.tool
def search_nodes(query: str, limit: int = 5) -> str:
    """
    Search for nodes in the knowledge graph by keyword.
    :param query: Search text to match against node labels, types, and descriptions.
    :param limit: Maximum number of results.
    :return: Formatted search results.
    """
    return graph.search_nodes(query, limit)


@toolbox.tool
def find_path(source: str, target: str) -> str:
    """
    Find the shortest path between two nodes in the knowledge graph.
    :param source: Label or ID of the starting node.
    :param target: Label or ID of the ending node.
    :return: The path as a sequence of edges, or a message if no path exists.
    """
    return graph.find_path(source, target)


@toolbox.tool
def graph_summary() -> str:
    """
    Get a summary of the knowledge graph: node count, edge count, most connected nodes.
    :return: Graph statistics.
    """
    return graph.get_summary()


# --- Slash command handler ---

SLASH_HELP = """Available commands:
  /graph              - Show graph summary
  /connections <name> - Show connections for a node
  /path <a> -> <b>    - Find shortest path between two nodes
  /save               - Save conversation transcript to file
  /export             - Export graph in Graphviz DOT format
  /help               - Show this help message
  /exit               - Save and exit"""


def _save_transcript() -> str:
    save_dir = Path('conversations')
    save_dir.mkdir(exist_ok=True)
    timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
    filepath = save_dir / f'chat_{timestamp}.md'

    # Load agent config for metadata
    agent = current_agent.get() or {}
    model = agent.get('model', 'unknown')
    prompt = agent.get('prompt', '')

    lines = [
        f'# Chat Session',
        f'',
        f'- **Model**: {model}',
        f'- **Saved**: {time.strftime("%Y-%m-%d %H:%M:%S")}',
        f'- **Graph**: {len(graph._nodes)} nodes, {len(graph._edges)} edges',
        f'',
    ]

    # System prompt
    if prompt:
        lines.append('## System Prompt')
        lines.append('')
        lines.append(prompt.strip())
        lines.append('')

    # Conversation with tool calls
    lines.append('## Conversation')
    lines.append('')

    for entry in transcript:
        if entry['type'] == 'user':
            lines.append(f'**User:** {entry["content"]}')
            lines.append('')
        elif entry['type'] == 'assistant':
            lines.append(f'**{entry.get("name", "Assistant")}:** {entry["content"]}')
            lines.append('')
        elif entry['type'] == 'tool_call':
            args = json.dumps(entry['arguments'], indent=2)
            lines.append(f'**Tool Call:** `{entry["name"]}({args})`')
            lines.append('')
        elif entry['type'] == 'tool_result':
            output = entry['output']
            if len(output) > 500:
                output = output[:500] + '...'
            lines.append(f'**Tool Result** (`{entry["name"]}`): {output}')
            lines.append('')

    # Usage statistics
    if usages:
        lines.append('## Usage Statistics')
        lines.append('')
        from usage import _aggregate_usage, _calculate_cost_usd
        totals = _aggregate_usage(usages)
        for model_name, total in totals.items():
            lines.append(f'### {model_name}')
            for key, value in total.items():
                lines.append(f'- {key.title()} (tokens): {value}')
            cost = _calculate_cost_usd({model_name: total})
            lines.append(f'- Cost (USD): ${cost:.6f}')
            lines.append('')
        total_cost = _calculate_cost_usd(totals)
        lines.append(f'**Total cost (USD):** ${total_cost:.6f}')
        lines.append('')

    filepath.write_text('\n'.join(lines))
    graph.save()
    return f'Conversation saved to {filepath}.'


def _handle_slash_command(cmd: str) -> str | None:
    parts = cmd.strip().split(maxsplit=1)
    command = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ''

    if command == '/graph':
        return graph.get_summary()

    if command == '/connections':
        if not arg:
            return 'Usage: /connections <node name>'
        return graph.get_connections(arg)

    if command == '/path':
        if '->' not in arg:
            return 'Usage: /path <source> -> <target>'
        src, tgt = arg.split('->', 1)
        return graph.find_path(src.strip(), tgt.strip())

    if command == '/save':
        return _save_transcript()

    if command == '/export':
        dot = graph.export_dot()
        export_path = Path('.graph_memory/graph.dot')
        export_path.write_text(dot)
        return f'DOT file written to {export_path}\n\n{dot}'

    if command == '/help':
        return SLASH_HELP

    if command == '/exit':
        return None

    return f'Unknown command: {command}\n{SLASH_HELP}'


# --- Main ---

usages: list = []


async def main(config_path: Path, debug: bool):
    _configure_logging(debug)
    client = AsyncOpenAI()

    agent = yaml.safe_load(config_path.read_text())

    print('Graph Memory Chatbot')
    print(f'Graph: {len(graph._nodes)} nodes, {len(graph._edges)} edges loaded')
    print('Type /help for available commands.\n')

    response = await run_agent(
        client, toolbox, agent,
        usage=usages,
    )

    if response:
        print(response)

    graph.save()
    print()
    print_usage(usages)


def _configure_logging(debug: bool) -> None:
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
    for logger_name in ('__main__', 'run_agent', 'tools', 'usage', 'graph_memory'):
        logging.getLogger(logger_name).setLevel(local_level)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Graph Memory Chatbot')
    parser.add_argument('config', type=Path, nargs='?', default=Path('graphbot.yaml'))
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    asyncio.run(main(args.config, args.debug))
