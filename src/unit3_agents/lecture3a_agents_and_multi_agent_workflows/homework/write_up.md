# Homework 3a

Build an agent workflow—multiple agents called in a hard-coded sequence.
Look back over the tasks from earlier in the semester:
can you solve them better with multiple agents?
Try different workflow structures;
experiment with both simple and complex orchestration

## Part 0: Reviewing Class Notes

I noticed that the provided agentic engineering files are set up in a yaml format.
It looks like the multi-agent descripcopy that information into tion follow this format:

```yaml
agents:
  - name: name of agent
    description: description of agent
    model: model choice
    prompt: |
      system prompt defining the agent's role, tone, and guardrails
    tools: [ tools that can be used by the agent ]
    kwargs: additional settings

  - name: ...
```

## Part 1: Building an agent workflow

*Initial concept*: Here is my idea, my plan is to create a multi-agent system that
will allow a user to provide any fictional story and will find a way to create a plausible
placement of Hoid in that story and where to look for him and what he was doing.

*Note: Hoid is a fictional character of Brandon Sanderson's design who is a character
who according to Brandon Sanderson is always around usually as a random nondescript
background character, but he always has a plan and is up for something.*

### Step 1: Designing an Architecture

1. The User should be able to interact with a historian like agent that keeps track of Hoid's exploits
2. That historian user-facing agent should have access to a research agent that compiles plot details,
   naming conventions, and unnamed side characters from the user requested story. It will do this uing web-search
3. Another agent will be the Hoid-disguiser, it will have access to the output of the researcher agent and
   also access to a Hoid information file. Useing these two points of context it will place Hoid in the user-provided
   story in a convincing way that includes what Hoid was up to
4. Finally, the historian agent will present the location, name, and motives of Hoid in the user provided scene

### Step 2: Building the Hoid fact-file

I am using the provided example multi-agent research example to generate a usable fact-file describing Hoid's
motivations, names, and general characteristics/abilities so that the Hoid disguiser agent will be able to
effectively placed in the stories.

### Step 3: Build the Program

Using AI I modified deep_research.py to be hoid_was_here.py and I created a skeleton hoid_was_here.yaml which
I then filled with the appropriate prompts.

### Step 4: Testing the Program

## Conclusion

### What I Learned

I found that in building this multi-agent system that planning where I am going beforehand makes it easier to
work through the building process. I also found that making asyncrounus calls to OpenAI's API made the
implementation of the reasearch part of the tool more functional that way it doesn't get caught in a bottle-neck.
From a Python perspective I found that to import files in different directories I have to provide the import
paths. Somethng else I learned was that to interupt a python program you cannot use ^C in pychram.
I found that getting the agent's tone right invovled putting specific limits on what their tasks were.
The hardest part was getting the agents to not try to take on each other's tasks. I found that my making it clear
what theiur responsibilities were in their prompts made it go smoother.

### Things to Try in the Future

I think it would be interesting to play around with the jail-breaking homework to see if I would build a labrinth of
agents that stops the user from ever getting around the guardrails.

