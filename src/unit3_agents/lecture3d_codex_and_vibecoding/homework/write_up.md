# Lecture 3a

## Part 0: Experience with Agent-Assisted Coding

I have seen in the past that coding agents are not very good at working
with large projects in depth without first organizing the information.
In the past I have used Claude Code, so I am used to a CLAUDE.md instead
of an AGENTS.md, but they serve the same purpose.

I have found that compressing the context when I finish a significant
task usually works a little better than letting it auto compress, but
it is very similar. Something agent-assisting coding is very good at
is following instructions, this is also a downside. I have found that
if I tell it to fix a specific bug it will give me a quick and dirty
fix rather than something that is "good coding" for the project at
large unless that is specified as part of the request.

## Part 1: Experimenting with Codex

Following the in class example, I asked codex to build me a web-based
version of a game I enjoyed playing in high-school. It is a dice game
called Equations made by the AGLOA.

Notes:

* It is interesting, Codex was willing to search the web for the game
  rules but when it could not find the specific of one of the rules
  it put that on me to find.
* Because the game is obscure it took a few revisions of the plan to
  make it possible for Codex to actually implement the idea.
* We did not discuss skills in class, so I am guessing that it will be
  a part of the next lecture and homework.
* I did look through the skill creation menu.
* I am surprised at how well Codex was able to implement this dice game.
* I like Claude's default building of an AGNETS.md file better than
  Codex's. This is because Claude gives organized explanations for what
  is used any why. Codex seems to give more of an overview. I probably
  could get comparable results by modifying the way I prompt it.
* I just tested it and `/init` does yield similar results. Hmmm, I wonder
  if there is a way to get that behavior without calling `/init`
* I wonder if there is a difference in the effectiveness based on the
  model. I am using `gpt-5.2-codex`

## Part 2: Working on my Project

I have successfully built a GUI for my project for user interaction.
I also have successfully set up a successful system for transcribing
pdfs and txt files into chunks to repare them for the RAG implementation
that I am doing next.