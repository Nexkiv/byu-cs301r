# Lecture 2f

## Preparatory Reading

In preparation for discussion I read the two readings:

* [Agentic Misalignment (Anthropic)](https://www.anthropic.com/research/agentic-misalignment)
* [Training LLMs for Honesty via Confessions](https://cdn.openai.com/pdf/6216f8bc-187b-4bbb-8932-ba7c40c5553d/confessions_paper.pdf)

## Playing Around with MCP Servers

Using Claude Code, I had it walk me through the MCP creation process using FastMCP. This way I could see what each piece
was doing. With this I built a simple trivia MCP server. As part of the creation process using Claude a testing file was
also built. In doing so I learned that it is possible to make calls to MCP servers even if you are not an agent. That
was interesting and made a lot of sense. Based on this I will want to design accurate tests when I build MCP servers in
the future. One challenge I faced is that for OpenAI to call the MCP server it needs to be publicly visible. Another
issue that I ran into was that the model wasn't naturally figuring out that it could call the mcp server, so it was
getting lost in trying to use the python coding tool (see `chat_15-42-35.md). Something interesting that I came across
was that making mcp server calls is substantially less expensive than generating responses. In the end I was able to get
the server mostly running; however, I couldn't get the ducktales trivia section to work properly. That is an area to
spend further time on.