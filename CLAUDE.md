# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a BYU CS 301R course repository for **Agentic Engineering**. It contains class materials and homework assignments organized by course units, focusing on prompt engineering and multi-agent workflows using OpenAI's API.

## Project Structure

```
src/
├── unit1_prompt_engineering/
│   └── lecture1a_intro_to_completion/
│       ├── class_material/      # Examples and utilities for basic completion
│       └── homework/            # Student homework assignments
└── unit3_agents/
    └── lecture3a_agents_and_multi_agent_workflows/
        ├── class_material/      # Agent framework and examples
        └── homework/            # Multi-agent workflow assignments
```

## Environment Setup

- Create a `.env` file with `OPENAI_API_KEY=your_key_here` (see `.env.example`)
- This repository uses OpenAI's API (models: gpt-5.2, gpt-5.1, gpt-5, gpt-5-mini, gpt-5-nano, gpt-4.1 series)
- Python dependencies are managed without a formal requirements file; common imports include `openai`, `yaml`, `asyncio`

## Running Code

### Unit 1: Basic Completions

Run completion scripts from their directory:
```bash
cd src/unit1_prompt_engineering/lecture1a_intro_to_completion/class_material
python basic_response.py
python text_processor.py
```

For homework completion app:
```bash
cd src/unit1_prompt_engineering/lecture1a_intro_to_completion/homework
python completion_app.py prompt.md --model gpt-5-nano
```

### Unit 3: Multi-Agent Workflows

Run agent workflows from the class_material directory:
```bash
cd src/unit3_agents/lecture3a_agents_and_multi_agent_workflows/class_material
python deep_research.py [config.yaml]
```

The agent framework expects YAML config files as arguments (defaults to `deep_research.yaml` if not specified).

## Architecture

### Agent Framework (Unit 3)

The multi-agent system uses a YAML-based configuration approach:

**Core Components:**
- `run_agent.py`: Main agent execution loop that handles tool calls and message history
- `tools.py`: ToolBox class for registering and invoking tools with strict JSON schemas
- `usage.py`: Token usage tracking and cost calculation utilities

**Agent Configuration Format (YAML):**
```yaml
agents:
  - name: agent_name
    description: what the agent does
    model: gpt-5-mini
    prompt: |
      system prompt defining role and behavior
    tools: [web_search, custom_tools]
    kwargs:
      text:
        format:
          type: json_schema
          name: response_name
          schema: {...}
```

**Key Patterns:**
- Agents run in orchestrated sequences (not autonomous loops)
- JSON parsing includes repair logic for unescaped quotes (`_repair_unescaped_quotes`)
- Async execution for parallel agent calls using `asyncio.gather()`
- Tools are registered via `@toolbox.tool` decorator with automatic schema generation
- `web_search` is a special built-in tool type

**Typical Workflow Structure:**
1. Chat agent for user interaction
2. Planning/expansion agent for task decomposition
3. Executor agent(s) for parallel task execution
4. Synthesis agent for final output aggregation

### Completion API Pattern (Unit 1)

Simple request/response using `client.responses.create()`:
- Uses `input` parameter (string or message list)
- `reasoning={'effort': 'low'}` for basic completions
- Always track usage with `print_usage(model, response.usage)`

## Common Development Tasks

### Running Tests
No test framework is currently configured in this repository.

### Adding New Agents
1. Define agent configuration in YAML following the format in `deep_research.yaml`
2. Create orchestration script similar to `deep_research.py`
3. Use `run_agent()` function from `run_agent.py` for execution
4. Track usage across all agent calls with shared `usage` list

### Adding Custom Tools
Register tools in the ToolBox with type annotations:
```python
@toolbox.tool
def your_tool(param: str, optional_param: int | None = None) -> str:
    """Tool description for LLM."""
    return result
```

Tool schemas are auto-generated from type hints. Only `str`, `int`, `float`, `bool`, and `Literal` types are supported.

## Token Usage and Cost

All scripts include token usage tracking via `usage.py`:
- Prints input, cached, output, and reasoning token counts
- Calculates cost in USD based on pricing table (updated Dec 2025)
- Available as `print_usage()` for console output or `format_usage_markdown()` for structured output

Model pricing ranges from $0.05/1M input tokens (gpt-5-nano) to $21/1M input tokens (gpt-5.2-pro).
