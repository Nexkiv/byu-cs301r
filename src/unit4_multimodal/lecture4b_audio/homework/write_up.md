# Lecture 4b

## Continuing Work on the Project

Glorious day! I have finally fixed the problem I was having in ingesting, embedding, and pulling files from my RAG
system for my chat. It will now accurately pull from the study guides and compose a complete list of terms or people
that I need to know. Some key design decisions that I made were to make sure that the parser of the uploaded files does
it in a way that is not fine-tuned to the specific training study guide. Initially I was aggressively modifying the
system prompts to improve behavior; however, the fix only worked when I took a step back and changed the way that it was
chunking and used a programmatic approach. I have also scrubbed by codebase of the code debt built up from the old
Gradio implementation. I also improved the file/class deleation workflow so that it now will remove everything, so I no
longer have to worry about dangling files upon deletion.

This change fixed the problems I was having with the chat feature; however,
the flashcard generation feature is currently broken now, so that is what I will work on next time. I will also work on
other fixes to prepare it to be demo worthy.

