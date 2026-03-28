# Lecture 1c

## Part 1: Build a chatbot

I based my chatbot on the one from the class notes.
I added a chat saving functionality to the program so that I could save the chats for the next phases.
As mentioned below I had to make modifications so it could work with Greek.
I also added a chat saving functionalityh that will allow me to be able to save the conversation to a seperate file.

## Part 2: Design a complex role

The first complex persona that I built was a Greek language tutor.
From this I learned that Greek letters are not included in 'utf-8', so I had to modify the code.
This is being used to test the ability for the chat-bot to keep track of multiple languages.
It also was a test to see if I could implant ulterior motives (notice how I told the chat-bot to say everything comes
from Greek, think Big Fat Greek Wedding)
I was not very successful at the secondary goal. `chat_10-11-51.md`

My second complex persona is a band instructor who can write music.
Or at least thinks it can. I don't give it access to music writing software but the prompt implies that I did.
The chat-bot generated an xml formated version of the sheet music; however, it was formatted incorrectly so it wouldn't
work.
This experiment has shown me how a llm will be confident if the engineer gives it a reason to be confident even if it
doesn't have the requisite functionality. `chat_10-21-58.md`

## Part 3: Reliably reproduce a hallucination

I used the classic seahorse emoji question, and it gave me a jelly-fish emoji initially.
I then played around with trying to convince it further that the emoji exists.
I did this by playing around with emojis outside the training set.
I was unsuccessful in my attempt. `chat_10-34-42.md`

## Part 4: Design a prompt that requires the bot to fulfill a sequence of tasks

I played around with building an inefficient math solver prompt.
The way I did this was by defining a list of tasks that are intended to distract the model or to be arbitrary in nature.
I was unable to force the model to work out of order by not keeping track of the completed tasks.
`chat_10-42-52.md`

## Future ideas

I think it would be interesting to play around with an llm's ability to provide post-hoc justification for its answers.
I think it will be interesting to see if I can get some unintended behavior by exploiting that.

