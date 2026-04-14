# Lecture 2e

## Part 1: OpenAI's built-in tools

I played around with OpenAI's websearch tool. I mostly tried asking questions on niche topics that are recent. This had
success, and I was able to have the model successfully call web search. The prompting of the model was intended to be
simple and it seems to work. Oddly it kept hitting a wall when trying to access some BYU resources because it was
pulling from some obscure BYU sub site. It also was not accurately finding the information from the page (see
`chat_12-37-17.md`). This appears to be a limitation of web_search where the model can get lost in a rabbit hole if it
thinks it found an answer.

## Part 2: run python tool

I played around with some of the prompts from lecture2d. It seems like the model isn't willing to give a python
executable unless it "thinks" it really doesn't know the answer. That was a little surprising (see `chat_12-52-36.md`).
I then modified the prompt to try to get the model to be more willing to use python. That seemed to improve it
partially. The human-in-the-loop style authentication also worked successfully where it wouldn't run Python code without
getting permission first.

## Part 3: Real world resources with human-in-the-loop + run python tool

I had Claude Code build me some dummy files that I could then play around with using the human in the loop system and to
try having it write some python and running it. I was able to get the chatbot to make a python script to assemble
information into a plot using Python. It also exhibited human-in-the-loop functionality (see `chat_17-26-21.md`). I
tried again with the `inventory.json` dataset and even when I provided it with the JSON structure it refused to read in
the data even though it should be able to seeing as the GPA plotting worked (see `chat_17-38-15.md`). I found that when
I outlined all the important information, the chatbot was willing to use its execute Python skill to do this search
(see `chat_17-43-05.md`).