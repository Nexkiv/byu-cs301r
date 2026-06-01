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

### Section 3e: Harness Engineering

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

### Section 3f: Cookbook and Advanced Structure

* Explain the differences between working memory, episodic memory, and semantic memory.
    * Working memory is the short-duration active store that hold all information currently in use during a task.
      It is the memory relating to the current conversation, this includes the context of the conversation
      and what has been said relating to recent tasks. This also includes the agent's reasoning state, tool call
      results, intermediate outputs, and any injected system prompts. In short, working memory is the active context
      window of the agent.
    * Episodic memory is a type of long-term memory that stores records of specific past events, anchored in time and
      context. It relates to the specific events or experiences of the user. This involves the logs of previous
      conversations or a vector database of the embeddings of past scenarios. This is used for keeping track of the
      context of those past events. This allows for the agent to be able to use context from past sessions to
      contextualize the current task. Episodic memory retrieval is
      commonly done using a vector database in a similar way to how a RAG system works. Episodic memory would be used
      when a user is working on a new math problem because the agent would be able to reference past conversations
      solving math problems and would follow the same flow that the previous interactions had.
    * Semantic memory is a type of long-term memory that stores stable, general facts and knowledge independent of any
      specific event. It is where specifics about the user or scenario are stored across sessions. For example, a model
      would default to explain how to use an app in the Linux OS if in a previous conversation the user stated that they
      work primarily in the Linux OS. Semantic memory is how responses from the agent can stay fine-tuned to the user.
      It is usually implemented using a persistent key-value store or user profile database.
* Explain why memory compaction is valuable.
    * Memory compaction is the process by which the active information of a conversation is compressed to a smaller,
      more manageable amount, to improve the effectiveness of the agent. It is usually triggered when the model
      approaches a soft threshold of its capacity, like 70-80% or after key milestones like when a task is completed.
      Memory compaction serves three purposes. It is used to save information into long-term memory. By compacting
      memory, it gets added to episodic and semantic memory to be used later. This allows facts to permeate
      conversations without being needed to be saved to the working memory every time they are brought up. The second
      advantage of memory compaction is that it keeps the context of the conversation robust so the model doesn't get
      affected by context drift. This is important because all models have a context limit where they can only hold a
      certain number of tokens in their context at a time. This way the model can keep track of the most important
      pieces of information and compress the "noise" that contains low-signal content or redundant context. Another
      advantage is that it helps to highlight information that could be "lost in the middle" of a long set of context.
      By compacting the memory this could be kept relevant. The downside of memory compaction is similar to the downside
      of image compression, although it offers advantageous benefits, it also comes with the cost of losing information.
      This loss of information could also lead to the problem that it is trying to solve with compacting to preserve "
      lost in the middle" information if the model does not see it as important during the compaction process. Memory
      compaction would involve saving completed tasks to long-term memory and then replacing the building process with a
      simple summary and also removing etiquette words like please and thank you and instead storing the politeness of
      the user and expected politeness of the model in long-term memory.

### Section 3g: Evaluation and Security

* What do we mean by "LLM as judge"? Describe when you'd use it.
    * LLM-as-judge is a system where an agent's response is graded by an LLM typically by returning a structured output
      containing a score and reasoning for the score. This is similar to agent-as-judge which is a system where outputs
      generated by an agent are then graded by a different agent that has access to tools, reasoning steps, and has the
      ability to verify outputs at each stage of the workflow. This paradigm is used when attempting to improve the
      quality of responses in a subjective way. One way these systems can be used is in determining if a response would
      answer the user's question. If a user asks for a list of Mexican restaurants and then an agent provides a list,
      the judge agent can then verify those listings to see if they should qualify as valid Mexican restaurants. Another
      use case for an LLM-as-judge system is evaluating tone, safety, or style. In an agent-as-judge
      system, it can verify responses against source documents using a RAG system. Another use case is that these judge
      systems can be the first step in limiting human-in-the-loop systems. For example, if a user asks an agent to
      write a database query, the judge agent can read through the generated code and validate it against major security
      flaws. This would allow the user to only need to validate queries that have a bigger danger window. One more use
      case is for scalable automated testing. Instead of extensive human annotators during model evaluation, an
      LLM-as-judge system can provide preliminary scoring of the model to pipeline regression testing.
* Name 2 or 3 considerations to be careful of or mitigate when using LLM as judge.
    * One downside of the agents-as-judge approach is that it takes much longer for the user to get back a response,
      because there is a back and forth between the generative agent and the judging agent. The way to mitigate this
      problem is to cache results for reoccurring output patterns or running the judge asynchronously. Another downside
      of agent-as-judge is the systematic bias of the judge itself. The judge could be biased by elements that are only
      tangentially connected to the quality of the response. These features include the output length, which output
      came first, and favoring a response that matches the judge's style. To mitigate this problem, is to use a
      calibrated judge or to use multiple judges that have different requirements and then average the scores. A third
      consideration that should be made is on the goal of the evaluation. When something is evaluated it either is
      evaluated subjectively or objectively. They are also evaluated against solutions that have grounded truth
      per-example or no grounded truth per-example. When attempting to evaluate a model against a use case where there
      is a per-example grounded truth, it might be more effective to use a deterministic system instead of an
      LLM-as-judge. When evaluating subjective responses it is important that the goals are clearly outlined especially
      in cases where there is no per-example grounded truth. For example, evaluating if a logic problem solution is
      correct has a per-example grounded truth and should use a deterministic checker. On the other hand,
      evaluating the empathic response of a customer service agent has no grounded truth, so it lends itself better to
      an LLM-as-judge approach. To mitigate goal misalignment, it is important to establish a rubric with explicit
      criteria before deploying the judge.
* Briefly describe how you might turn an evaluation metric into a guardrail.
    * The purpose of an evaluation metric is for the grading of the response of a model. A guardrail is instead for the
      enforcement of some standard at runtime by blocking or regenerating an output on failure to comply. Guardrails can
      be applied as sanitization or filtering of the incoming message from the user or on limiting the response from the
      agent. One application of an evaluation metric being used as a guardrail could be in the setting of a pass/fail
      threshold. This threshold could then be used to enforce the guardrail on the conversation or agent use. an example
      of this would be a toxicity rating of an LLM's response to a user. This can be evaluated using an LLM-as-judge,
      and it will give a score back that if it meats a threshold like 0.7 or higher it forces a regeneration. This
      regeneration request would also include specifics about why it failed in an attempt to get a valid new output. A
      similar, but different approach would be to implement a deterministic check on the output to be able to grade the
      response and force it to be regenerated if it does not meet the criteria. A use case based on this system would be
      building a deterministic evaluation system that checks the LLMs output for words or phrases that it should never
      use and then force a regeneration or ask the user for clarification. For example if building a tutor bot, if it is
      never supposed to give the user code it could run a check on the output for coding syntax and then if it sees
      coding syntax it could flag the system and force regeneration. In both examples a retry limit could be applied to
      reduce the likelihood of the generation and judge system getting caught in a loop with each other.
* Name 2-3 prompt injection attacks
    * Prompt injection attacks are where a user is able to give an agent context that would get it to act in a way that
      is against its intended design.
    * A direct prompt injection attack follows the same structure as a SQL injection attack with the intent on
      overriding access or action. In a SQL injection attack you can force the database to drop tables by formatting
      your input in a way that gets it to run the malicious command. In a similar way, using an LLM you can inject the
      model to ignore its previous instruction and then redirect it onto a different path. This is usually done to
      override the input guardrails. The attack attempts to override the main agent's system prompt instruction by
      injecting conflicting commands in the user input. One potential mitigation can be partially achieved by using
      instruction hierarchy enforcement. This involves giving clear restrictions in the system prompt that force the LLM
      to override potentially malicious requests from the user. The downside of this approach is that it is still based
      on the effectiveness of the system prompt which is only a probabilistic mitigation.
    * Another type of prompt injection attack is an indirect approach where it isn't the user giving the agent the
      injection prompt, but instead it comes from another source. This can occur when an agent has access to websearch
      and then scrapes those pages for information. This can lead to injection prompts being read into the context.
      Indirect prompt injection attacks can be mitigated by separating trusted and untrusted context. This would work by
      keeping system context at highest security, user input at potentially dangerous, and data read in from external
      sources as high risk. This would limit the effect of dangerous injections from untrusted sources.
    * Another kind of injection is multimodal injection. This involves embedding malicious instructions in images,
      audio, or PDFs that the agent processes. These injections can be hazardous because possibly the user doesn't
      recognize the malicious instructions in the files, but they will be passed to the model. An example of this is
      white fronting. This is the process of hiding instructions usually in PDFs in text written in a white font color.
      These could be any malicious instructions, similar to a direct injection attack. To mitigate this risk, it
      is important to sanitize all modes of information passed into the model. This can be done in multiple ways: a
      modal sandbox where each mode of information is processed in an isolated context; applying the same content
      policies on the extracted text that text input has to run through; and treating all derived content as untrusted
      by default.

### Section 4a: Images

* Why might you use a two-step image generation workflow where a model first generates an output and then reflects on it
  before producing a second image?
    * This type of system has two main types of implementations. The first is an iteration based approach where the
      first image that is generated is a rough outline of the final image. This is similar to a difusion model; however,
      the difference is that with a two or multistep image generation workflow that happens in phases, it is a secondary
      model that provides feedback and descriptions on how to improve in the next phase. Iteration is an important part
      of agentic development and by applying that principle to image generation, the ability to generate a higher
      quality final product is higher. This works because the model is reflecting on the parts that are generated first
      so it is able to refine its performance. A specific advantage of two-step image generation is that it allows for
      images to be produced in phases. This mimics the traditional creation of images where first forms are established,
      then surrounding features, and finally refinement of the shapes and colors. This advantage works because the model
      is also generating in parts the agent will be able to focus on clean up and details on the second pass. The other
      type of two-image generation would involve the initial generation of an image and then the holistically critiquing
      of the image by a separate agent to result in an improved final image being generated. This process works
      similarly to LLM-as-judge where the reflection step generates structured feedback for the generation model. This
      workflow allows for prompt alignment checking. By getting a complete image, the model can then grade it and
      establish criteria for the second image generation. Another advantage of this method is that it makes it possible
      for guardrails to be applied as a part of the refinement process before the final image is generated to redirect
      the process of generating the image to be within the restrictions. By critiquing an image the model can also
      establish visual consistency in the generated image that would have been missed in the initial generation of the
      image.
* What are two ways to pass image data to a model for analysis?
    * The two methods of passing an image to a model for analysis are by providing the model with a URL that points to
      the image or by sending the image directly using Base64 encoding. The URL approach keeps the
      payload lightweight while the Base64 approach embeds the entire raw image. Both methods require the image to be of
      a format that the model can handle (usually PNG, JPEG, GIF, and WebP).
    * URL: The first method is to provide the model with a url that points directly to the image. This is done by using
      a specific part of the model's API to send it the image. For example, it could follow the format:
      `{"type": "image_url", "image_url": {"url": "https://..."}}` An advantage of the URL approach is that enables the
      cahching of the image's URL to save on context. A weakness of this method is that the model must be
      able to access the URL at inference time. This means that images that are hosted privately or locally will fail.
    * Base64 encoding: The other method is by sending the image as a Base64-encoded string. This allows the user to send
      the image to the model directly from a local file or a dynamically generated image. The weakness of this method is
      that it greatly increases the size of the payload. This will increase latency and can result in failure to use the
      API, because it will hit the request size limit for large images. Another disadvantage is that the image will fill
      up the context of the conversation because the model will have to hold onto it. This will result in an increased
      token cost and usage.

### Section 4b: Audio

* Compare and contrast the realtime speech-to-speech architecture vs the speech-to-text to text-to-speech architecture.
    * Realtime speech-to-speech architecture is a system that allows a user to send audio to the model and to then have
      it interpret it and provide an audio response. The speech-to-text to text-to-speech architecture is a system where
      the user's audio input is first transformed into text and then passed to the model. The model then returns a text
      response which is then converted to speech on the user's side.
    * Speech-to-speech architecture is able to have a quicker response time because all the analysis of the speech can
      be handled on the model's end making it possible for the model's side to make optimizations. This advantage gives
      speech-to-speech an approximate 85% speed up improvement. Another advantage of speech-to-speech is that it is able
      to handle the tone and intonation of the user's input better because the model has access to that information. A
      third advantage is that a speech-to-speech system is able to handle barge-in requests and stop generating mid
      sentence to replicate the real flow of conversation. One drawback of the system is that it is not customizable
      because all the components are done on the model's side. Another drawback is that this architecture does not allow
      for the ability to debug the text because it is handled on the model's side. Another disadvantage is that this
      system costs more than speech-to-text to text-to-speech because the model has to host all the tools for processing
      the input and it charges for that process.
    * The speech-to-text to text-to-speech architecture is most effective at adding additional context to the user
      inputs before passing them on to the model. The main disadvantage of this architecture is it slows the process
      because there is a hand-off between the speech-to-text system to the llm and then a hand-off from the llm to the
      text-to-speech system. Another disadvantage of this method is that it easily
      propagates transcription errors. If the transcription of the user's audio is bad it is compounded when it is
      passed to the model as pure text.