# Lecture Lecture 3f

## Part 1: Learn about common frameworks for agents

* LangChain's LangGraph: This uses agent workflows are directed graphs with typed state. Nodes are agents or functions
  while edges are transitions and conditional routing.
* LlamaIndex: This framework is based on microservices and is service-oriented. The thing that it is best at is data
  integration and RAG routing.
* CrewAI: This framework is structured towards role-based collaboration. It is best for setting up muti-agent teams.
* n8n: n8n is unique because ir is built on visual nodes. The biggest advantage is that it is easier for integration in
  teams where they are built in a low code system.
* AutoGen: This framework is based on asynchronous messaging where tasks can be accomplished across language models and
  system boundaries. This framework works best when a task requires the agents to be long-running.
* PydanticAI: This one is a Python framework. It is focused on predictable and structured outputs. For this reason it is
  what a framework of choice in scenarios where type-safe structured outputs is what is needed.

## Part 2: Build Something Fun

I wanted to build an agent memory model that worked similar to a graph where memories would be stored as nodes that
connected to other memories. This is a trial run of something that I am playing around with for my project's chatbot
feature. My build of the memory system leads to long tool calls in an attempt to continually check the graph and
to make connections. In the future I will play around with making the graph memory more streamlined to improve the user
experience.

## Part 3: Progress on the Project

I implemented the 4th phase which included flash card generation based on the RAG model and generated terms. This took
some modification to get working. I still haven't gotten it to pull all the terms from a RAG search that is something
that I will work on in future phases. To get the UI to function properly, it took several iterations using Claude Code
and direct modifications of the codebase. 