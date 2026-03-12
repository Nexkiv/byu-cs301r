# Homework 3b

Build a chat that has both input and output guardrails

## Part 1: Architecture

Chat interface:

Chat: history, current prompt

Initial architecture design idea:

1. Default opening message
2. User provides input
3. user input gets cleaned by the **cleaning agent** and then passed onto the **responding agent**.
4. responding agent generates a response to the query
5. responding agent passes that response to the **quality control agent**
6. quality control agent checks the generated response to gauge its compliance
7. if the message is compliant
    * The control agent gives the message to the user.
    * Otherwise, the control agent prompts forward the response to the cleaning agent with clarifying remarks (step 3)
    * *Note: if this step is reached three times, the user is given an unable to respond message*
8. the user's next input is given to the cleaning agent again, repeat from step 3.

## Part 2: Writing the script

Using the defined architecture, I wrote up a censor.yaml file that has the agents for the system to work.
I then gave this context to Claude code and worked with it on creating a python script that would put it into
effect. To implement the structure I was having difficulty using agent assisted programming because initially
it wanted to copy the format of agents.py which would lead to a security risk.

### Part 1: When a user mentions a taboo topic, the prompt gets additional emphasis on how to respond

My initial implementation of this idea involved having an initial processing agent whose responsibility is
to clean the user's input.

### Part 2: When the agent returns data that is invalid/incorrect, the agent is prompted with the feedback to try again.

My initial implementation of this idea was done in a sub agent that handled the creation of the response.
By separating out the response generator, I could delegate the output cleansing to a different agent
that had that specific responsibility.

## End-notes

I was unsuccessful in making a successful censoring system. I think it is most likely because I used an
agents-as-tools system. In the future, if I have time, I might play around with other ways to pull this off.
One obvious downside is that getting a response takes substantially longer when there are these cleaning
and prepping agents involved.

## Future Ideas

It would be cool to host this taboo censoring chat using gradio and then give it to other students to see if
they can break through and get it to violate its rules.

I think it would also be interesting to try to build a more secure version of this where I hard code agent calls
for part of it instead of using agents-as-tools to handle it, because this is less secure.