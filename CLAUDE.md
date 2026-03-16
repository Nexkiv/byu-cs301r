# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a BYU CS 301R course repository for **Agentic Engineering**. It contains class materials and homework assignments organized by course units, focusing on prompt engineering, tool calling, RAG systems, and multi-agent workflows using OpenAI's API.

## Project Structure

```
src/
├── unit1_prompt_engineering/
│   ├── lecture1a_intro_to_completion/
│   │   ├── class_material/      # Basic completion API usage
│   │   └── homework/            # Completion app with prompts
│   ├── lecture1b_prompt_engineering/
│   │   ├── class_material/      # Few-shot, structured output, YAML configs
│   │   └── homework/            # Enhanced completion app
│   ├── lecture1c_chat/
│   │   └── class_material/      # Chatbot with Gradio UI, personas
│   ├── lecture1d_jailbreaking/
│   │   └── class_material/      # Adversarial prompts, agent conversations
│   ├── lecture1e_reasoning/
│   │   └── class_material/      # Chain-of-thought, reasoning display
│   └── lecture1f_discipleship/  # Ethics discussion (no code)
│
├── unit2_agent_tools/
│   ├── lecture2a_rag/
│   │   └── class_material/      # Embeddings, vector search (Jupyter)
│   ├── lecture2b_rag_solutions/
│   │   └── class_material/      # ChromaDB, document chunking
│   ├── lecture2c_ethics/        # Ethics discussion (no code)
│   ├── lecture2d_tool_calling/
│   │   └── class_material/      # Function calling, ToolBox class
│   ├── lecture2e_real_world_impact/
│   │   └── class_material/      # Docker containers, code execution
│   ├── lecture2f_mcp_and_alternatives/
│   │   └── class_material/      # MCP servers, FastMCP, AWS Lambda
│   └── lecture2g_ethics/        # Ethics discussion (no code)
│
├── unit2.5_midterm/             # Midterm assessment questions
│
├── unit3_agents/
│   ├── lecture3a_agents_and_multi_agent_workflows/
│   │   ├── class_material/      # YAML-based multi-agent orchestration
│   │   └── homework/            # Multi-agent storytelling workflow
│   ├── lecture3b_agents_as_tools/
│   │   ├── class_material/      # Agents calling agents dynamically
│   │   └── homework/            # Content censorship workflow
│   └── lecture3c_class_project/ # Project planning (no code)
│
└── unit4.5_final/               # Final assessment questions
```

## Environment Setup

- Create a `.env` file with `OPENAI_API_KEY=your_key_here` (see `.env.example`)
- This repository uses OpenAI's API (models: gpt-5.2, gpt-5.1, gpt-5, gpt-5-mini, gpt-5-nano, gpt-4.1 series)
- Python dependencies are managed without a formal requirements file; common imports include:
  - `openai` - OpenAI Python client
  - `yaml` - Configuration files
  - `asyncio` - Async/parallel execution
  - `gradio` - Web UIs for chatbots
  - `chromadb` - Vector database (Unit 2)
  - `langchain` - Text splitting utilities (Unit 2)
  - `fire` - CLI generation (Unit 2)
  - `fastmcp` - MCP server framework (Unit 2f)

## Running Code

### Unit 1: Prompt Engineering

**Basic Completions (Lecture 1a):**
```bash
cd src/unit1_prompt_engineering/lecture1a_intro_to_completion/class_material
python basic_response.py
python text_processor.py
```

**Homework App:**
```bash
cd src/unit1_prompt_engineering/lecture1a_intro_to_completion/homework
python completion_app.py prompt.md --model gpt-5-nano
```

**Enhanced Completion with YAML (Lecture 1b):**
```bash
cd src/unit1_prompt_engineering/lecture1b_prompt_engineering/class_material
python file_input.py
```

**Chatbot (Lecture 1c):**
```bash
cd src/unit1_prompt_engineering/lecture1c_chat/class_material
python chatbot.py --web                    # Launch Gradio web UI
python chatbot.py                          # Console mode
python chatbot.py --role roles/role_tutor_college.md  # With specific persona
```

**Reasoning Chatbot (Lecture 1e):**
```bash
cd src/unit1_prompt_engineering/lecture1e_reasoning/class_material
python chatbot.py --show-reasoning --reasoning-effort medium
```

### Unit 2: Agent Tools

**RAG with Embeddings (Lecture 2a):**
```bash
cd src/unit2_agent_tools/lecture2a_rag/class_material
jupyter notebook "Embedding Workflow.ipynb"
```

**ChromaDB RAG (Lecture 2b):**
```bash
cd src/unit2_agent_tools/lecture2b_rag_solutions/class_material
python chroma_demo.py ingest_folder /path/to/documents  # Index documents
python chroma_demo.py query "your query here"           # Search
```

**Tool Calling Chatbot (Lecture 2d):**
```bash
cd src/unit2_agent_tools/lecture2d_tool_calling/class_material
python toolbot.py --web
```

**Code Execution in Docker (Lecture 2e):**
```bash
cd src/unit2_agent_tools/lecture2e_real_world_impact/class_material
python codebot.py
```

**MCP Server (Lecture 2f):**
```bash
cd src/unit2_agent_tools/lecture2f_mcp_and_alternatives/class_material/fastmcp_server
python mcp_server_stock.py  # Start MCP server
# In another terminal:
python call_stock_mcp.py    # Test MCP client
```

### Unit 3: Multi-Agent Workflows

**Orchestrated Agents (Lecture 3a):**
```bash
cd src/unit3_agents/lecture3a_agents_and_multi_agent_workflows/class_material
python deep_research.py                    # Uses deep_research.yaml
python deep_research.py custom_config.yaml # Custom config
```

**Agents as Tools (Lecture 3b):**
```bash
cd src/unit3_agents/lecture3b_agents_as_tools/class_material
python agents.py quotes.yaml
```

**Homework Examples:**
```bash
cd src/unit3_agents/lecture3a_agents_and_multi_agent_workflows/homework
python hoid_was_here.py  # Multi-agent storytelling

cd src/unit3_agents/lecture3b_agents_as_tools/homework
python censor.py         # Content censorship workflow
```

## Architecture

### Unit 1: Prompt Engineering Patterns

**Basic Completion (Lecture 1a):**
```python
from openai import Client
client = Client()
response = client.responses.create(
    model="gpt-5-nano",
    input="Your prompt here",
    reasoning={'effort': 'low'}
)
print_usage(model, response.usage)
```

**Chat Pattern (Lecture 1c):**
```python
history = []
history.append({"role": "system", "content": persona_prompt})
history.append({"role": "user", "content": user_message})
response = client.responses.create(model="gpt-5-mini", input=history)
history.append({"role": "assistant", "content": response.text})
```

**Reasoning Pattern (Lecture 1e):**
```python
response = client.responses.create(
    model="gpt-5-mini",
    input=prompt,
    reasoning={'summary': 'auto', 'effort': 'medium'},
    stream=True
)
for chunk in response:
    if hasattr(chunk.reasoning_summary_text, 'delta'):
        print(chunk.reasoning_summary_text.delta, end='')
```

### Unit 2: Tool Calling Architecture

**ToolBox Class (Lecture 2d):**
```python
from tools import ToolBox

toolbox = ToolBox()

@toolbox.tool
def my_tool(param: str, count: int = 1) -> str:
    """Tool description for the LLM."""
    return f"Result: {param * count}"

# Tool schemas auto-generated from type hints
# Supports: str, int, float, bool, Literal, Optional types
```

**Tool Calling Loop (Lecture 2d):**
```python
while True:
    response = client.responses.create(
        model="gpt-5-mini",
        input=history,
        tools=toolbox.tools
    )

    if response.type == "message":
        break  # Done
    elif response.type == "function_call":
        result = toolbox(response.name, response.arguments)
        history.append({
            "role": "tool",
            "tool_call_id": response.id,
            "content": result
        })
```

**Docker Code Execution (Lecture 2e):**
```python
# Runs Python in isolated container with:
# - No network access (--network none)
# - Resource limits (CPU, memory, PIDs)
# - Read-only filesystem + /tmp tmpfs
# - Non-root user execution
# - Timeout enforcement
```

**MCP Server (Lecture 2f):**
```python
from fastmcp import FastMCP

mcp = FastMCP("Server Name")

@mcp.tool()
def my_mcp_tool(query: str) -> str:
    """Tool accessible via MCP protocol."""
    return result

# Deploy to AWS Lambda or run locally
```

### Unit 3: Multi-Agent Architecture

**YAML-Based Agent Configuration (Lecture 3a):**
```yaml
agents:
  - name: researcher
    description: Researches topics in depth
    model: gpt-5-mini
    prompt: |
      You are a thorough researcher. Use web_search to find information.
      Always cite sources and provide detailed analysis.
    tools: [web_search]
    kwargs:
      text:
        format:
          type: json_schema
          name: research_result
          schema:
            type: object
            properties:
              findings:
                type: array
                items:
                  type: object
                  properties:
                    fact: {type: string}
                    source: {type: string}
              summary: {type: string}
            required: [findings, summary]
```

**Agent Execution (Lecture 3a):**
```python
from run_agent import run_agent
from tools import ToolBox

toolbox = ToolBox()
usage = []

result = await run_agent(
    config=agent_config,
    toolbox=toolbox,
    usage=usage,
    user_message="Research quantum computing"
)

print(result)  # JSON-parsed output
print_usage(model, usage)
```

**Orchestrated Multi-Agent Workflow (Lecture 3a):**
```python
# Sequential execution
chat_result = await run_agent(chat_config, toolbox, usage, user_input)
plan_result = await run_agent(plan_config, toolbox, usage, chat_result)

# Parallel execution
tasks = [
    run_agent(researcher1_config, toolbox, usage, task1),
    run_agent(researcher2_config, toolbox, usage, task2),
    run_agent(researcher3_config, toolbox, usage, task3)
]
results = await asyncio.gather(*tasks)

# Synthesis
final = await run_agent(synthesizer_config, toolbox, usage, results)
```

**Agents as Tools Pattern (Lecture 3b):**
```python
from agents import as_tool, talk_to_user, conclude

# Wrap agents as callable tools
agent_tools = [
    as_tool(joking_agent_config),
    as_tool(research_agent_config),
    talk_to_user,  # Human-in-the-loop
    conclude       # End workflow
]

toolbox.register_tools(agent_tools)

# Main agent dynamically calls sub-agents
result = await run_agent(main_agent_config, toolbox, usage)
```

**Key Differences:**
- **Lecture 3a**: Pre-orchestrated sequence (you control flow)
- **Lecture 3b**: Dynamic delegation (agent controls flow)

## Common Development Tasks

### Running Tests
No test framework is currently configured in this repository.

### Adding New Agents (Unit 3)

**For Orchestrated Workflows (3a):**
1. Define agent configuration in YAML following the format in `deep_research.yaml`
2. Create orchestration script similar to `deep_research.py`
3. Use `run_agent()` function from `run_agent.py` for execution
4. Track usage across all agent calls with shared `usage` list
5. Use `asyncio.gather()` for parallel agent execution

**For Agent-as-Tools (3b):**
1. Define each sub-agent in YAML (can use multi-document format with `---`)
2. Load all agent configs from YAML
3. Wrap sub-agents with `as_tool()` function
4. Register wrapped agents in ToolBox
5. Create main agent that delegates to sub-agents
6. Include `talk_to_user` for human interaction, `conclude` to end workflow

### Adding Custom Tools (Unit 2)

Register tools in the ToolBox with type annotations:
```python
from tools import ToolBox

toolbox = ToolBox()

@toolbox.tool
def your_tool(param: str, optional_param: int | None = None) -> str:
    """Tool description for LLM."""
    return result
```

Tool schemas are auto-generated from type hints. Only `str`, `int`, `float`, `bool`, `Literal`, and `Optional` types are supported.

**Special Tools:**
- `web_search`: Built-in tool type, doesn't need registration
- `talk_to_user`: Built-in for human-in-the-loop (Unit 3b)
- `conclude`: Built-in to end agent workflow (Unit 3b)

### Building RAG Systems (Unit 2)

**With ChromaDB:**
```python
from chroma_demo import ingest_folder, query_whole_documents

# Index documents
ingest_folder("/path/to/docs", collection_name="my_docs")

# Query and retrieve full documents
results = query_whole_documents("your query", collection_name="my_docs")
```

**Key Considerations:**
- Chunk size impacts retrieval quality
- Use `RecursiveCharacterTextSplitter` for better chunking
- Retrieve whole documents from chunk matches
- Supports `.txt`, `.md`, `.py`, `.js`, `.java`, `.cpp`, `.h`, `.cs`, `.rb`, `.go`, `.rs`, `.php`, `.swift`, `.kt`, `.yml`, `.yaml`, `.json`, `.xml`, `.html`, `.css`, `.sql`, `.sh`

### Creating MCP Servers (Unit 2f)

```python
from fastmcp import FastMCP

mcp = FastMCP("ServerName")

@mcp.tool()
def tool_name(param: str) -> str:
    """Tool accessible via MCP protocol."""
    return result

# Run locally or deploy to AWS Lambda with Terraform
```

## Token Usage and Cost

All scripts include token usage tracking via `usage.py`:
- Prints input, cached, output, and reasoning token counts
- Calculates cost in USD based on pricing table (updated Dec 2025)
- Available as `print_usage()` for console output or `format_usage_markdown()` for structured output

Model pricing ranges from $0.05/1M input tokens (gpt-5-nano) to $21/1M input tokens (gpt-5.2-pro).

**Usage Pattern:**
```python
from usage import print_usage

usage = []  # Shared across all calls

response = client.responses.create(...)
usage.append(response.usage)

# For agents, pass usage list to run_agent()
await run_agent(config, toolbox, usage, message)

# Print at end
print_usage(model, usage)
```

## Key Technologies by Unit

### Unit 1: Prompt Engineering
- OpenAI Python Client (`Client`)
- Gradio (web UIs)
- YAML (configurations)
- Asyncio (streaming)

### Unit 2: Agent Tools
- OpenAI Embeddings API (`text-embedding-3-small`)
- ChromaDB (vector database)
- LangChain (`RecursiveCharacterTextSplitter`)
- Docker (code isolation)
- FastMCP (MCP server framework)
- Terraform (infrastructure as code)
- AWS Lambda (MCP deployment)
- Fire (CLI generation)
- Jupyter Notebooks

### Unit 3: Agents
- OpenAI AsyncOpenAI (parallel execution)
- Asyncio (`asyncio.gather()`)
- YAML (agent configurations, multi-document format)
- Custom agent framework (`run_agent.py`, `tools.py`)
- JSON schema validation
- Context variables

## Notable Files and Utilities

**Used Across Multiple Lectures:**
- `usage.py` - Token tracking and cost calculation (appears in ~10 lectures)
- `tools.py` - ToolBox class for function calling (Unit 2d-2f, Unit 3)
- `run_agent.py` - Agent execution loop (Unit 3)

**Chatbot Evolution:**
- `lecture1c_chat/chatbot.py` - Basic chat with Gradio
- `lecture1e_reasoning/chatbot.py` - Chat with reasoning display
- `lecture2d_tool_calling/toolbot.py` - Chat with tools
- `lecture2e_real_world_impact/toolbot.py` - Chat with code execution
- `lecture2f_mcp_and_alternatives/mcpbot.py` - Chat with MCP

**Multi-Agent Systems:**
- `lecture3a/.../deep_research.py` - Research workflow (5 agents, sequential + parallel)
- `lecture3a/.../hoid_was_here.py` - Storytelling workflow (5 agents with Hoid character)
- `lecture3b/.../agents.py` - Agent-as-tool orchestration (dynamic delegation)

## Homework Pattern

Each homework typically includes:
- Main Python script (e.g., `completion_app.py`, `hoid_was_here.py`)
- Configuration files (YAML or markdown prompts)
- `write_up.md` - Student reflections and analysis
- `homework.zip` - Submission package

## Assessment Files

- `unit2.5_midterm/` - Essay questions on Units 1-2
- `unit4.5_final/` - Essay questions on Unit 3

## Common CLI Patterns

**Completion Apps:**
```bash
python completion_app.py prompt.md --model gpt-5-nano
python completion_app.py classifier.yaml  # YAML config
```

**Chatbots:**
```bash
python chatbot.py --web                    # Gradio UI
python chatbot.py --role roles/file.md     # With persona
python chatbot.py --show-reasoning         # Display reasoning
python chatbot.py --reasoning-effort high  # Reasoning effort level
```

**Agent Workflows:**
```bash
python deep_research.py [config.yaml]  # Default or custom config
python agents.py quotes.yaml           # Agent-as-tools
```

**RAG Tools:**
```bash
python chroma_demo.py ingest_folder /path  # Index
python chroma_demo.py query "search term"  # Search
```

## Troubleshooting

**Missing API Key:**
- Ensure `.env` file exists with `OPENAI_API_KEY=your_key_here`
- Check `.env.example` for format

**Import Errors:**
- Most scripts expect to be run from their own directory
- Change to the lecture's `class_material/` directory before running

**Docker Issues (Lecture 2e):**
- Ensure Docker daemon is running
- Build container with scripts in `docker/` directory
- Check Docker permissions

**MCP Server Issues (Lecture 2f):**
- Ensure FastMCP dependencies installed
- Check server URL configuration
- Verify `require_approval` settings

**Agent Configuration Errors (Unit 3):**
- Validate YAML syntax (indentation matters)
- Ensure JSON schemas are valid
- Check agent names match tool references
- Verify `web_search` is in tools list if needed
