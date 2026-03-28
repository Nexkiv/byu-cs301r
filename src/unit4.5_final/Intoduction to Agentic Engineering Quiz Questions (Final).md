# Introduction to Agentic Engineering Quiz Questions (Final)

## Unit 3 Agents

### Section 3a: Agents and Multi-agent Workflows

* What are the key characteristics of an agent and why do each matter?
    * An agent has a few key characteristics, autonomy, goal-orientation, tool use, memory, context awareness, and
      self-correction. Autonomy is what enables workflows by giving the model the ability to complete multi-step tasks.
      This process makes the model not reliant on additional human input and reducing bottlenecks. The goal orientation
      is what keeps the model on task and focused on the outcome. By being goal oriented, the model is capible of
      creating a multi-step plan based on the provided high-level goal. The model also has access to actions through its
      ability to access tools. This gives it access to deterministic and up-to-date information. By having access to
      memory, the agent is able to have its actions persist across steps and sessions. Agents also are able to update
      their plan as they go which is an example of their context awareness behavior. It does this by observing the
      results of its actions rather than following a fixed plan blindly. Agents are also able to recover from
      intermediary failures without human intervention.
* Describe how you might use an agent workflow to solve the following problems: - Loan application processing system -
  Travel planning system (flights, hotels, car, tours/activities)
    * Loan application processing system: I would most likely use the hub approach. I would start by defining a banker
      agent that would be responsible for processing the loan. I would then give it access to a tool that lets it query
      past loans and another research agent that would be able to asemble information about the applicant from public
      and private sources. I would also set up the agent to log each of its actions so it can be trackible for future
      reference. For the final steps of loan approval, I would include a human-in-the loop system because it is a
      high-stakes task. I would then format the output in a way that lists the full action trail.
    * Travel planning system: The travel planning system would be built upon an agent that is set up with a travel agent
      personality. It would then give it access to tools that can pull information from sites like yelp and
      trip-advisor. I would also give it access to the Google Maps mcp where it could pull travel information. I would
      then layout the system in a way that would make it possible for the user of the service to provide contunual
      information relative to their travel plans as the agent asks them clarifying questions. I would also format the
      final output in a way that would be easy for the user to implement as a travel plan.

### Section 3b: Agents-as-Tools

* In what situations would agents-as-tools be a good fit?
    * The paradigm of agents-as-tools describes a system where agents are calling other agents. This differs from
      multi-agent workflows because there is not a pre-determined path that specifically calls agents but instead it is
      the agent that are calling other agents. Agents-as-tools are most effective when used in a workflow that is not
      deterministic and the decision for choosing flow cannot be chosen before-hand. This means that when working on a
      problem where there is a large amount of data and the actions that should be taken are relative to the data itself
      it might be best to build a system where an agent delegates tasks to other agents. Agents-as-tools is also useful
      when prototyping a usage design. Although a multi-agent workflow might work better, if the initial process is done
      using agents-as-tools you can then observe the way the task was accomplished and then create a multi-agent
      workflow from that.
* In what situations would agents-as-tools NOT be a good fit?
    * There are two main situations where agents-as-tools are not a good fit. First, in situations where a non-agentic
      solution would be better. For example when the situation would require a deterministic output like determining if
      a number is prime or solving a logic problem. As a general rule, agentic systems should not be used when they do
      not add enough of a benefit to overcome the added latency and hallucination risk introduced. Second, in situations
      where it is better suited to be solved by a multi-agent workflow. In a multi-agent workflow the order of calling
      agents and which ones are called is predetermined. Multi-agent workflows and agent-as-tools systems allow for
      domain expertise, parallel execution, and context window management. A downside of agents-as-tools systems is that
      they lead to unpredictability in the tools that are called. This would be a risk in high-stakes workflows. A
      specific example would be the calling of a guardrail agent that checks and modifies another agent's output to
      conform to security or safety standards. In that case, it would be unsecure to leave the calling of the guardrail
      agent up to the orchestrator because it could lead to it not being called. Another case in which agents-as-tools
      would not be a good fit is when building a sequentially-dependent workflow. For example in a system that has
      functionality for an authenticated user it must authenticate the user before providing that functionality.

```python
def talk_to_user(message: str):
    """
    Use this function to communicate with the user.
    All communication to and from the user **MUST**
    be through this tool.
    :param message: The message to send to the user.
    :return: The user's response.
    """
    _agent = current_agent.get()
    name = _agent['name'] if _agent else 'Agent'
    print(f'{name}: {message}')
    return input('User: ')
```

* How does the `talk_to_user` tool work and in what situations is it valuable?
    * The `talk_to_user` tool is a synchronous human-in-the-loop tool that can be provided to an agent allowing it to
      send messages to the user and receive responses. It does this by identifying which agent is making the request and
      what the request is, the tool then receiving input from the user. The purpose of this tool is to make it possible
      for any agent in the agent call stack that has been provided with this tool to be able to communicate with the
      user. This is useful because it makes it possible for each agent to handle its isolated context without requiring
      the agents to share relative context with the orchestrator every time they need input or clarification from the
      user. Another advantage of this tool is it reduces the chances of hallucination because if an agent needs further
      information it can ask the user rather than generating incorrect information. If this tool was used in a research
      agents-as-tools system, it would enable a research agent to be able to ask a follow-up question to the user
      relating to the research within its purview. Another circumstance where this tool would be useful is in a file
      management agentic-system. Because the deletion of files is a permanent action, the ability for a sub-agent to
      clarify and validate the deletion of files in its allocated directory helps to improve the security and robustness
      of the system.
* You need a marketing campaign plan that considers information from various sources, such as competitive analysis,
  budget, target audience, etc. *(Describe a multi-agent system that could build an effective marketing campaign.)*
    * I would build a system that leverages an agentic orchestrator to be able to consider information from various
      sources. The orchestrator would be tasked with creating a plan and a list of specific tool calls to other agents
      to gather the information. Each sub agent would be given a specific focus area to target by the orchestrator.
      Agents that need access to general up-to-date information would be given access to a web-search tool. Agents that
      would need specific information relating to my campaing would do so by making requests to an agent that has access
      to the campaign information. This campaign specific-knowledge agent would also have access to a tool that could be
      used to ask the people in charge of the campaign clarifying questions. This way it can leverage its ability to
      search the campaign information and provide accurate responses to the agents. The agents in charge of budget would
      be given access to tools that allow them to query previous performance metrics and current estimates.

### Section 3d: Codex and Vibecoding

* Why is the codex code sandbox important?
    * The codex sandbox is a constrained working environment that enforces boundaries on what codex can read, modify,
      and execute on your system. One benefit is that the codex sandbox helps to protect the other files outside your
      working directory. This makes it so codex does not accidentally modify files it shouldn't as established by the
      user or get access to confidential information. The sandbox environment also allows the user to set specific
      actions that are and are not allowed in the session. This makes it so the user does not get a request from codex
      every time it wants to take an action that the user has already whitelisted. The sandbox also limits codex's
      network connectivity providing a barrier to prompt injecting that could come as a result of accessing content on
      the network. Because LLMs are nondeterministic the sandbox also helps to create an established technical boarder
      that protects the system so it isn't left up to the model's judgment. The codex sandbox also gives the user a
      sense of security which makes them more willing to give codex more agentic access.
* Why does codex ask whether you trust a folder?
    * When you open codex in a new directory you haven't accessed before codex gives the user a warning about the
      current directory and asks the user if they trust its contents. This is a safety system similar to how when you
      open a new directory in vs-code it asks if you trust its authors. For executing untrusted code, if you run
      malicious code it could put your computer at serious risk. For example, a malicious AGENTS.md file could get
      interpreted by codex as legitimate commands and could lead to deletion of files or worse. For codex there is the
      added layer that all text is a possible route for prompt injection so when codex reads through the files a
      malicious actor could get codex to do some things that would put the user's system at risk.
* Why is the default network restriction important?
    * Codex is limited in its capabilities to be able to connect to the network. This has two main benefits. First, it
      establishes the sandbox environment that gives the user a sense of security for their codebase. Second, it stops
      codex from accessing untrusted websites that could be hosting untrusted information that could be used as a prompt
      injection. This is a risk because when an llm has web access it usually not only traverses the website for context
      but also its sub-pages and linked pages. This is a major risk because any of those could be harboring dangerous
      commands as explained in the previous question.
* You are tasked with building a simple web version of a favorite boardgame. *Describe how you would go about using
  Codex to accomplish this.*
    * I would start by switching codex into plan mode. I would then provide the name of the board game and a general
      idea of what level of quality I would want it built to. Then I would let it run and give me clarifying questions.
      I would then answer those questions in depth and any following questions. Once it give me a plan I would read
      through it and provide clarifications or modifications as I see fit. I would then allow it to execute the pan in
      suggest mode that way I can see each file change and ask questions about them if I don't understand why certain
      changes are being made. Once I have a completed web-app, I would play around with it. If I wanted to make further
      changes I would switch back to plan mode and iterate on this process until I have the web-app working the way I
      want it to.

## Section 3e: Harness Engineering

* What is an agent skill? How is it defined? How is it used?
    * An agent skill is a portable, reusable package of domain knowledge and procedural instructions that teaches an
      agent how to accomplish a specific workflow. Skills are defined with meta-data (front-matter) and context. The
      front-matter contains a name and description. They are used by the main instance of the model to identify the
      skill and when it should be used. The skill context includes what the skill does when it is included. They usually
      contain step-by-step instructions, output format requirements, relevant logic, or preferences on what resources to
      use. Skills are used by giving the model access to the list of skills usually by using an AGENTS.md. The agent
      then calls load_skill to pull skills based on their front-matter for specific circumstances. Skills are distinct
      from tools in that tools are capabilities while skills are instructions. Skills are also distinct from MCP in that
      MCP gives agents access to external tools and data while skills give the agent information on how to use those
      tools.
* Describe harness engineering. What is it? What goal does it seek to achieve?
    * Harness engineering is the process of building a system of skills that agents can pull from. The harness entry
      point is the AGENTS.md file where it describes the skill architecture to the agent. A harness can be thought of as
      the infrastructure of the repository, similar to an environment. This is because an environment provides runtime
      dependencies while harnesses provide behavioral/knowledge dependencies. Harness engineering allows a user to
      selectively load the relevant context using the skills that they make available to their agents. Harness
      engineering solves the context bloating problem by offloading the context of specific know-how into skills that
      will be accessed by the model when they are needed.
* What is progressive disclosure? Why is it important?
    * Progressive disclosure is an interaction design pattern that is built upon the concept that information should
      only be revealed when it is relevant, not all at once. In an agentic sense, progressive disclosure is the process
      that gives an agent control over when and what context is loaded. Progressive disclosure involves agents that have
      access to the specific skills that outline the know-how for tasks. When an agent accesses a skill, it allows it to
      access that context progressively. This solves the problem of context bloating where an agent's context would get
      filled with irrelevant context that could distract or confuse the agent. By making the context something that is
      added only when it is needed it makes it so the agents can stay on track easier. Progressive disclosure has three
      parts: (1) the skill index with only the names and descriptions from AGENTS.md, (2) the full skill context loaded
      from the skill file, (3) deep supporting materials that are accessed only when they are needed. The biggest
      drawback of progressive disclosure is that it increases the latency of the agent. This happens because the model
      has to make an inference to match the task to a skill and then invoke `load_skill` before proceeding.
* Describe the principle of agent legibility. Why is it important? What does it aim to accomplish?
    * Agent legibility is the concept that the actions taken by an agent should be able to be seen and parsed by a human
      user. This includes both what the agent does and why it does it. Some ways that this principle is applied is in
      the use of structured logging, chain-of-though-output, step-by-step updates, or audit trails. This principle makes
      it possible for users to better understand what is happening and when to shift the process being performed by the
      agent to avoid context drift and agentic misalignment. Another advantage of agent legibility is that it makes the
      process of debugging the agents actions clearer to the user. When the agent fails at a task, if it was performed
      legibly, then the user would be able to trace the process to find where the error occurred. Another advantage is
      that it allos for trust and auditability which is essential in high-stakes workflows. Agent legibility is used to
      make human-in-the-loop more effective by keeping the actions performed by the agent clear to the user. The goal of
      agent legibility is to make human oversight of a system possible in a way that enables the effective application
      of human judgment.